import { Application } from '@splinetool/runtime';

export const handleSplineLoad = (spline: Application) => {
  try {
    // Set initial camera position
    spline.setZoom(1.5);
    
    // Optional: Set camera target
    // spline.setTarget(-50, 0, 0);
    
    // Optional: Set camera rotation
    // spline.setRotation(0, 0, 0);
    
    // Disable orbit controls for auth pages
    const canvas = spline.canvas;
    if (canvas) {
      canvas.style.pointerEvents = 'none';
    }
  } catch (error) {
    console.error('Error setting up Spline scene:', error);
  }
};
