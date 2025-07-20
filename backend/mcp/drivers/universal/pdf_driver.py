"""
PDF Driver - Handles PDF file operations
Supports: read, create, merge, split, extract text, add watermark
"""

import logging
import asyncio
import io
import os
from typing import Dict, Any, List, Optional, Union
import base64
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

try:
    import PyPDF2
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

class PdfDriver(BaseUniversalDriver):
    """Universal driver for PDF file operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "pdf_driver"
        self.supported_node_types = [
            'n8n-nodes-base.pdf',
            'pdf.read',
            'pdf.create',
            'pdf.merge',
            'pdf.split',
            'pdf.extract_text',
            'pdf.add_watermark',
            'pdf.get_info'
        ]
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        base_params = ['operation']
        if node_type in ['pdf.read', 'pdf.split', 'pdf.extract_text', 'pdf.get_info']:
            base_params.append('file_path')
        elif node_type in ['pdf.create']:
            base_params.append('content')
        elif node_type in ['pdf.merge']:
            base_params.append('file_paths')
        return base_params
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if not DEPENDENCIES_AVAILABLE:
            return {
                "success": False,
                "error": "PDF dependencies not available. Install: pip install PyPDF2 reportlab"
            }
        
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            operation = parameters.get('operation', node_type.split('.')[-1] if '.' in node_type else 'read')
            
            if operation == 'read':
                return await self.read_pdf(parameters, context)
            elif operation == 'create':
                return await self.create_pdf(parameters, context)
            elif operation == 'merge':
                return await self.merge_pdfs(parameters, context)
            elif operation == 'split':
                return await self.split_pdf(parameters, context)
            elif operation == 'extract_text':
                return await self.extract_text(parameters, context)
            elif operation == 'add_watermark':
                return await self.add_watermark(parameters, context)
            elif operation == 'get_info':
                return await self.get_pdf_info(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def read_pdf(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Read PDF file"""
        self.logger.info("Reading PDF file")
        
        try:
            file_path = parameters.get('file_path', '')
            
            # Handle file from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    if 'file_content' in input_data:
                        # Handle base64 encoded content
                        file_content = input_data['file_content']
                        if isinstance(file_content, str):
                            file_content = base64.b64decode(file_content)
                        return await self._read_pdf_from_bytes(file_content, parameters)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                pages = []
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    pages.append({
                        "page_number": page_num + 1,
                        "text": text
                    })
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "total_pages": len(pdf_reader.pages),
                    "pages": pages,
                    "metadata": pdf_reader.metadata if hasattr(pdf_reader, 'metadata') else {},
                    "message": f"Successfully read PDF with {len(pages)} pages"
                }
                
        except Exception as e:
            self.logger.error(f"PDF read failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _read_pdf_from_bytes(self, file_content: bytes, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read PDF from bytes"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            
            pages = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                pages.append({
                    "page_number": page_num + 1,
                    "text": text
                })
            
            return {
                "success": True,
                "total_pages": len(pdf_reader.pages),
                "pages": pages,
                "metadata": pdf_reader.metadata if hasattr(pdf_reader, 'metadata') else {},
                "message": f"Successfully read PDF with {len(pages)} pages"
            }
            
        except Exception as e:
            self.logger.error(f"PDF read from bytes failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_pdf(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create PDF file"""
        self.logger.info("Creating PDF file")
        
        try:
            content = parameters.get('content', '')
            output_path = parameters.get('output_path', 'output.pdf')
            page_size = parameters.get('page_size', 'letter')
            
            # Handle content from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    content = input_data.get('content', content)
                    output_path = input_data.get('output_path', output_path)
                elif isinstance(input_data, str):
                    content = input_data
            
            if not content:
                return {
                    "success": False,
                    "error": "Content is required to create PDF"
                }
            
            # Create PDF
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            # Set up text
            width, height = letter
            text_object = c.beginText(1*inch, height - 1*inch)
            text_object.setFont("Helvetica", 12)
            
            # Handle multi-line content
            lines = content.split('\n')
            for line in lines:
                text_object.textLine(line)
            
            c.drawText(text_object)
            c.save()
            
            # Save to file
            pdf_content = buffer.getvalue()
            buffer.close()
            
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
            
            return {
                "success": True,
                "output_path": output_path,
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "file_size": len(pdf_content),
                "message": f"Successfully created PDF: {output_path}"
            }
            
        except Exception as e:
            self.logger.error(f"PDF creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def merge_pdfs(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Merge multiple PDF files"""
        self.logger.info("Merging PDF files")
        
        try:
            file_paths = parameters.get('file_paths', [])
            output_path = parameters.get('output_path', 'merged.pdf')
            
            # Handle file paths from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, list):
                    file_paths = input_data
                elif isinstance(input_data, dict):
                    file_paths = input_data.get('file_paths', file_paths)
            
            if not file_paths or len(file_paths) < 2:
                return {
                    "success": False,
                    "error": "At least 2 file paths are required for merging"
                }
            
            # Verify all files exist
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "error": f"File not found: {file_path}"
                    }
            
            # Merge PDFs
            merger = PyPDF2.PdfWriter()
            
            for file_path in file_paths:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        merger.add_page(page)
            
            # Save merged PDF
            with open(output_path, 'wb') as f:
                merger.write(f)
            
            merger.close()
            
            return {
                "success": True,
                "input_files": file_paths,
                "output_path": output_path,
                "merged_files_count": len(file_paths),
                "message": f"Successfully merged {len(file_paths)} PDFs into {output_path}"
            }
            
        except Exception as e:
            self.logger.error(f"PDF merge failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def split_pdf(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Split PDF file"""
        self.logger.info("Splitting PDF file")
        
        try:
            file_path = parameters.get('file_path', '')
            output_dir = parameters.get('output_dir', 'split_pages')
            page_ranges = parameters.get('page_ranges', None)  # e.g., [[1, 3], [4, 6]]
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    output_dir = input_data.get('output_dir', output_dir)
                    page_ranges = input_data.get('page_ranges', page_ranges)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                
                output_files = []
                
                if page_ranges:
                    # Split by specified ranges
                    for i, (start, end) in enumerate(page_ranges):
                        writer = PyPDF2.PdfWriter()
                        
                        for page_num in range(start - 1, min(end, total_pages)):
                            writer.add_page(reader.pages[page_num])
                        
                        output_file = os.path.join(output_dir, f"pages_{start}-{end}.pdf")
                        with open(output_file, 'wb') as out_f:
                            writer.write(out_f)
                        
                        output_files.append(output_file)
                        writer.close()
                else:
                    # Split into individual pages
                    for page_num in range(total_pages):
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_num])
                        
                        output_file = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
                        with open(output_file, 'wb') as out_f:
                            writer.write(out_f)
                        
                        output_files.append(output_file)
                        writer.close()
                
                return {
                    "success": True,
                    "input_file": file_path,
                    "output_directory": output_dir,
                    "output_files": output_files,
                    "total_pages": total_pages,
                    "split_files_count": len(output_files),
                    "message": f"Successfully split PDF into {len(output_files)} files"
                }
                
        except Exception as e:
            self.logger.error(f"PDF split failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def extract_text(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract text from PDF"""
        self.logger.info("Extracting text from PDF")
        
        try:
            file_path = parameters.get('file_path', '')
            page_range = parameters.get('page_range', None)  # e.g., [1, 5]
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    page_range = input_data.get('page_range', page_range)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                
                if page_range:
                    start_page = max(1, page_range[0]) - 1
                    end_page = min(total_pages, page_range[1])
                else:
                    start_page = 0
                    end_page = total_pages
                
                extracted_text = []
                full_text = ""
                
                for page_num in range(start_page, end_page):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    extracted_text.append({
                        "page_number": page_num + 1,
                        "text": text
                    })
                    full_text += text + "\n"
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "total_pages": total_pages,
                    "extracted_pages": len(extracted_text),
                    "pages": extracted_text,
                    "full_text": full_text,
                    "character_count": len(full_text),
                    "message": f"Successfully extracted text from {len(extracted_text)} pages"
                }
                
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_watermark(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add watermark to PDF"""
        self.logger.info("Adding watermark to PDF")
        
        try:
            file_path = parameters.get('file_path', '')
            watermark_text = parameters.get('watermark_text', 'WATERMARK')
            output_path = parameters.get('output_path', 'watermarked.pdf')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    watermark_text = input_data.get('watermark_text', watermark_text)
                    output_path = input_data.get('output_path', output_path)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Create watermark PDF
            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer, pagesize=letter)
            c.setFillColorRGB(0.8, 0.8, 0.8)  # Light gray
            c.setFont("Helvetica", 40)
            c.drawCentredText(letter[0]/2, letter[1]/2, watermark_text)
            c.save()
            
            watermark_buffer.seek(0)
            watermark_pdf = PyPDF2.PdfReader(watermark_buffer)
            watermark_page = watermark_pdf.pages[0]
            
            # Apply watermark to original PDF
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                
                for page in reader.pages:
                    page.merge_page(watermark_page)
                    writer.add_page(page)
                
                with open(output_path, 'wb') as out_f:
                    writer.write(out_f)
                
                writer.close()
            
            watermark_buffer.close()
            
            return {
                "success": True,
                "input_file": file_path,
                "output_file": output_path,
                "watermark_text": watermark_text,
                "message": f"Successfully added watermark to PDF: {output_path}"
            }
            
        except Exception as e:
            self.logger.error(f"Watermark addition failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_pdf_info(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get PDF file information"""
        self.logger.info("Getting PDF information")
        
        try:
            file_path = parameters.get('file_path', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                info = {
                    "file_path": file_path,
                    "total_pages": len(reader.pages),
                    "file_size": os.path.getsize(file_path),
                    "metadata": {}
                }
                
                # Get metadata if available
                if hasattr(reader, 'metadata') and reader.metadata:
                    metadata = reader.metadata
                    info["metadata"] = {
                        "title": metadata.get('/Title', ''),
                        "author": metadata.get('/Author', ''),
                        "subject": metadata.get('/Subject', ''),
                        "creator": metadata.get('/Creator', ''),
                        "producer": metadata.get('/Producer', ''),
                        "creation_date": str(metadata.get('/CreationDate', '')),
                        "modification_date": str(metadata.get('/ModDate', ''))
                    }
                
                return {
                    "success": True,
                    **info,
                    "message": f"Successfully retrieved PDF information"
                }
                
        except Exception as e:
            self.logger.error(f"PDF info retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return ['read', 'create', 'merge', 'split', 'extract_text', 'add_watermark', 'get_info']
