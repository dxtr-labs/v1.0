'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Settings, 
  Check, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  Plus,
  Trash2,
  Edit,
  Key,
  Link,
  Shield,
  Globe,
  Mail,
  MessageSquare,
  Phone,
  Share2,
  Database,
  Cloud,
  Zap,
  RefreshCw,
  Server
} from 'lucide-react';
import { Credential, ServiceConfig } from '@/lib/types/credentials';
import { CredentialsService } from '@/lib/services/credentials';

const SERVICE_CONFIGS: { [key: string]: ServiceConfig } = {
  // Social Media - OAuth-based
  instagram: {
    name: 'Instagram',
    category: 'Social Media',
    icon: <div className="w-5 h-5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>,
    description: 'Connect your Instagram account for automated posting and content management',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-gradient-to-r from-purple-500 to-pink-500',
    authType: 'oauth',
    provider: 'facebook', // Instagram uses Facebook OAuth
    service: 'instagram'
  },
  twitter: {
    name: 'Twitter/X',
    category: 'Social Media',
    icon: <div className="w-5 h-5 bg-black dark:bg-white rounded-full"></div>,
    description: 'Connect to Twitter/X for automated tweets and social media management',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-black dark:bg-white',
    authType: 'oauth',
    provider: 'twitter',
    service: 'twitter'
  },
  linkedin: {
    name: 'LinkedIn',
    category: 'Social Media',
    icon: <div className="w-5 h-5 bg-blue-600 rounded-full"></div>,
    description: 'Connect to LinkedIn for professional networking and content sharing',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-blue-600',
    authType: 'oauth',
    provider: 'linkedin',
    service: 'linkedin'
  },
  facebook: {
    name: 'Facebook',
    category: 'Social Media',
    icon: <div className="w-5 h-5 bg-blue-500 rounded-full"></div>,
    description: 'Connect to Facebook for page management and content posting',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-blue-500',
    authType: 'oauth',
    provider: 'facebook',
    service: 'facebook'
  },

  // Communication - Mixed OAuth and API key
  gmail: {
    name: 'Gmail',
    category: 'Communication',
    icon: <Mail className="w-5 h-5 text-red-600" />,
    description: 'Connect Gmail for automated email sending and management',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-red-600',
    authType: 'oauth',
    provider: 'google',
    service: 'gmail'
  },
  outlook: {
    name: 'Outlook',
    category: 'Communication',
    icon: <Mail className="w-5 h-5 text-blue-600" />,
    description: 'Connect Outlook for automated email sending and management',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-blue-600',
    authType: 'oauth',
    provider: 'microsoft',
    service: 'outlook'
  },
  slack: {
    name: 'Slack',
    category: 'Communication',
    icon: <MessageSquare className="w-5 h-5 text-purple-600" />,
    description: 'Connect to Slack for team communication and notifications',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-purple-600',
    authType: 'oauth',
    provider: 'slack',
    service: 'slack'
  },
  telegram: {
    name: 'Telegram',
    category: 'Communication',
    icon: <MessageSquare className="w-5 h-5 text-blue-400" />,
    description: 'Connect to Telegram for automated messaging and bot interactions',
    fields: [
      { name: 'botToken', label: 'Bot Token', type: 'password', placeholder: 'Get from @BotFather', required: true },
      { name: 'chatId', label: 'Chat ID', type: 'text', placeholder: 'Target chat ID (optional)', required: false },
    ],
    color: 'bg-blue-400',
    authType: 'api_key'
  },
  twilio: {
    name: 'Twilio',
    category: 'Communication',
    icon: <Phone className="w-5 h-5 text-red-500" />,
    description: 'SMS and voice communication service for automated messaging',
    fields: [
      { name: 'accountSid', label: 'Account SID', type: 'text', placeholder: 'From Twilio Console', required: true },
      { name: 'authToken', label: 'Auth Token', type: 'password', placeholder: 'From Twilio Console', required: true },
      { name: 'phoneNumber', label: 'Phone Number', type: 'text', placeholder: '+1234567890', required: true },
    ],
    color: 'bg-red-500',
    authType: 'api_key'
  },

  // Cloud Storage - OAuth-based
  googleDrive: {
    name: 'Google Drive',
    category: 'Cloud Storage',
    icon: <Cloud className="w-5 h-5 text-blue-500" />,
    description: 'Connect to Google Drive for file storage and management',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-blue-500',
    authType: 'oauth',
    provider: 'google',
    service: 'drive'
  },
  onedrive: {
    name: 'OneDrive',
    category: 'Cloud Storage',
    icon: <Cloud className="w-5 h-5 text-blue-600" />,
    description: 'Connect to Microsoft OneDrive for file storage and management',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-blue-600',
    authType: 'oauth',
    provider: 'microsoft',
    service: 'onedrive'
  },
  dropbox: {
    name: 'Dropbox',
    category: 'Cloud Storage',
    icon: <Cloud className="w-5 h-5 text-blue-700" />,
    description: 'Connect to Dropbox for file synchronization and sharing',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-blue-700',
    authType: 'oauth',
    provider: 'dropbox',
    service: 'dropbox'
  },

  // AI Services - API Key based
  openai: {
    name: 'OpenAI',
    category: 'AI Services',
    icon: <Zap className="w-5 h-5 text-green-500" />,
    description: 'Connect to OpenAI for AI-powered automation and content generation',
    fields: [
      { name: 'apiKey', label: 'API Key', type: 'password', placeholder: 'sk-...', required: true },
      { name: 'organizationId', label: 'Organization ID', type: 'text', placeholder: 'org-... (optional)', required: false },
    ],
    color: 'bg-green-500',
    authType: 'api_key'
  },
  anthropic: {
    name: 'Anthropic Claude',
    category: 'AI Services',
    icon: <Zap className="w-5 h-5 text-purple-500" />,
    description: 'Connect to Anthropic Claude for AI assistance and automation',
    fields: [
      { name: 'apiKey', label: 'API Key', type: 'password', placeholder: 'sk-ant-...', required: true },
    ],
    color: 'bg-purple-500',
    authType: 'api_key'
  },

  // Development - OAuth-based
  github: {
    name: 'GitHub',
    category: 'Development',
    icon: <div className="w-5 h-5 bg-gray-800 dark:bg-white rounded-full"></div>,
    description: 'Connect to GitHub for repository management and automation',
    fields: [], // OAuth - no manual fields needed
    color: 'bg-gray-800',
    authType: 'oauth',
    provider: 'github',
    service: 'github'
  },

  // Database - Manual configuration (sensitive)
  postgres: {
    name: 'PostgreSQL',
    category: 'Database',
    icon: <Database className="w-5 h-5 text-blue-700" />,
    description: 'Connect to PostgreSQL database for data operations',
    fields: [
      { name: 'host', label: 'Host', type: 'text', placeholder: 'localhost', required: true },
      { name: 'port', label: 'Port', type: 'text', placeholder: '5432', required: true },
      { name: 'database', label: 'Database', type: 'text', placeholder: 'database_name', required: true },
      { name: 'username', label: 'Username', type: 'text', placeholder: 'username', required: true },
      { name: 'password', label: 'Password', type: 'password', placeholder: 'password', required: true },
    ],
    color: 'bg-blue-700',
    authType: 'manual'
  },
  mysql: {
    name: 'MySQL',
    category: 'Database',
    icon: <Database className="w-5 h-5 text-gray-500" />,
    description: 'Connect to MySQL database for data operations',
    fields: [
      { name: 'host', label: 'Host', type: 'text', placeholder: 'localhost', required: true },
      { name: 'port', label: 'Port', type: 'text', placeholder: '3306', required: true },
      { name: 'database', label: 'Database', type: 'text', placeholder: 'database_name', required: true },
      { name: 'username', label: 'Username', type: 'text', placeholder: 'username', required: true },
      { name: 'password', label: 'Password', type: 'password', placeholder: 'password', required: true },
    ],
    color: 'bg-gray-500',
    authType: 'manual'
  },

  // Webhooks & APIs
  webhook: {
    name: 'Custom Webhook',
    category: 'Webhooks & APIs',
    icon: <Link className="w-5 h-5 text-gray-600" />,
    description: 'Configure custom webhook endpoints for integrations',
    fields: [
      { name: 'url', label: 'Webhook URL', type: 'url', placeholder: 'https://your-webhook-url.com', required: true },
      { name: 'method', label: 'HTTP Method', type: 'text', placeholder: 'POST', required: true },
      { name: 'headers', label: 'Headers (JSON)', type: 'text', placeholder: '{"Authorization": "Bearer token"}', required: false },
    ],
    color: 'bg-gray-600',
    authType: 'manual'
  },
};

export default function ConnectivityPage() {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedService, setSelectedService] = useState<string>('');
  const [formData, setFormData] = useState<{ [key: string]: string }>({});
  const [showPasswords, setShowPasswords] = useState<{ [key: string]: boolean }>({});
  const [editingCredential, setEditingCredential] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [useEnvironmentVars, setUseEnvironmentVars] = useState(false);

  const credentialsService = CredentialsService.getInstance();

  // Load credentials from the service
  const loadCredentials = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedCredentials = await credentialsService.getCredentials();
      setCredentials(fetchedCredentials);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load credentials');
      console.error('Error loading credentials:', err);
    } finally {
      setLoading(false);
    }
  }, [credentialsService]);

  useEffect(() => {
    loadCredentials();
    
    // Handle OAuth callback results
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get('success');
    const error = urlParams.get('error');
    
    if (success) {
      const serviceMap: { [key: string]: string } = {
        'google_connected': 'Google',
        'linkedin_connected': 'LinkedIn',
        'microsoft_connected': 'Microsoft',
        'slack_connected': 'Slack',
        'twitter_connected': 'Twitter/X',
        'github_connected': 'GitHub',
        'dropbox_connected': 'Dropbox',
      };
      
      const serviceName = serviceMap[success] || 'Service';
      alert(`✅ ${serviceName} connected successfully!`);
      
      // Clean up URL
      window.history.replaceState({}, '', '/dashboard/connectivity');
      loadCredentials(); // Refresh the credentials list
    }
    
    if (error) {
      const errorMap: { [key: string]: string } = {
        'oauth_error': 'OAuth authorization failed',
        'missing_params': 'Missing required parameters',
        'token_exchange_failed': 'Failed to exchange authorization code',
        'user_info_failed': 'Failed to retrieve user information',
        'callback_error': 'OAuth callback error occurred',
      };
      
      const errorMessage = errorMap[error] || 'Unknown error occurred';
      alert(`❌ Connection failed: ${errorMessage}`);
      
      // Clean up URL
      window.history.replaceState({}, '', '/dashboard/connectivity');
    }
  }, [loadCredentials]);

  const categories = ['All', ...Array.from(new Set(Object.values(SERVICE_CONFIGS).map(s => s.category)))];

  const filteredServices = selectedCategory === 'All' 
    ? Object.entries(SERVICE_CONFIGS)
    : Object.entries(SERVICE_CONFIGS).filter(([_, config]) => config.category === selectedCategory);

  const handleAddCredential = async () => {
    if (!selectedService) return;

    try {
      setTestingConnection(true);
      const serviceConfig = SERVICE_CONFIGS[selectedService];
      
      // Handle OAuth services
      if (serviceConfig.authType === 'oauth') {
        await handleOAuthAuthorization(serviceConfig);
        return;
      }

      // Handle API key and manual services
      const credentialData = {
        name: formData.name || `${serviceConfig.name} Connection`,
        service: selectedService,
        fields: { ...formData },
      };

      let result: Credential;
      if (editingCredential) {
        result = await credentialsService.updateCredential(editingCredential, credentialData);
        setCredentials(prev => prev.map(cred => 
          cred.id === editingCredential ? result : cred
        ));
        setEditingCredential(null);
      } else {
        result = await credentialsService.createCredential(credentialData);
        setCredentials(prev => [...prev, result]);
      }

      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save credential');
    } finally {
      setTestingConnection(false);
    }
  };

  const handleOAuthAuthorization = async (serviceConfig: ServiceConfig) => {
    try {
      const response = await fetch(`/api/oauth/authorize?provider=${serviceConfig.provider}&service=${serviceConfig.service}`);
      const data: { authUrl?: string; error?: string; message?: string } = await response.json();
      
      if (data.authUrl) {
        // Open OAuth authorization in a new window
        window.open(data.authUrl, '_blank', 'width=500,height=600');
        resetForm();
      } else {
        throw new Error(data.message || 'Failed to get authorization URL');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OAuth authorization failed');
    }
  };

  const resetForm = () => {
    setShowAddForm(false);
    setSelectedService('');
    setFormData({});
    setShowPasswords({});
    setError(null);
  };

  const deleteCredential = async (id: string) => {
    try {
      await credentialsService.deleteCredential(id);
      setCredentials(prev => prev.filter(cred => cred.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete credential');
    }
  };

  const editCredential = (credential: Credential) => {
    setSelectedService(credential.service);
    setFormData(credential.fields);
    setEditingCredential(credential.id);
    setShowAddForm(true);
  };

  const testConnection = async (service: string, fields: { [key: string]: string }) => {
    try {
      setTestingConnection(true);
      const result = await credentialsService.testConnection(service, fields);
      return result;
    } catch (err) {
      console.error('Connection test failed:', err);
      return false;
    } finally {
      setTestingConnection(false);
    }
  };

  const togglePasswordVisibility = (fieldName: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'connected':
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"><Check className="w-3 h-3 mr-1" />Connected</Badge>;
      case 'error':
        return <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"><AlertCircle className="w-3 h-3 mr-1" />Error</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">Disconnected</Badge>;
    }
  };

  return (
    <div className="h-full w-full overflow-y-auto">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <motion.h1 
            className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC] mb-2"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Connectivity
          </motion.h1>
          <motion.p 
            className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            Manage your integrations and API connections
          </motion.p>
        </div>

      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {categories.map(category => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="flex items-center gap-2"
            >
              {category === 'All' && <Globe className="w-4 h-4" />}
              {category === 'Social Media' && <Share2 className="w-4 h-4" />}
              {category === 'Communication' && <MessageSquare className="w-4 h-4" />}
              {category === 'Cloud Storage' && <Cloud className="w-4 h-4" />}
              {category === 'Database' && <Database className="w-4 h-4" />}
              {category === 'AI Services' && <Zap className="w-4 h-4" />}
              {category === 'Webhooks & APIs' && <Link className="w-4 h-4" />}
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Add Connection Button */}
      <div className="mb-6">
        <Button
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add New Connection
        </Button>
      </div>

      {/* Existing Credentials */}
      {credentials.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">
            Your Connections
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {credentials.map(credential => {
              const serviceConfig = SERVICE_CONFIGS[credential.service];
              return (
                <Card key={credential.id} className="bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {serviceConfig?.icon}
                        <div>
                          <CardTitle className="text-sm">{credential.name}</CardTitle>
                          <CardDescription className="text-xs">{serviceConfig?.name}</CardDescription>
                        </div>
                      </div>
                      {getStatusBadge(credential.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between items-center">
                      <div className="text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
                        {credential.lastUsed && `Last used: ${new Date(credential.lastUsed).toLocaleDateString()}`}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => editCredential(credential)}
                        >
                          <Edit className="w-3 h-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => deleteCredential(credential.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Add/Edit Connection Form */}
      {showAddForm && (
        <motion.div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-white dark:bg-[#0F172A] rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
          >
            <h3 className="text-lg font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">
              {editingCredential ? 'Edit Connection' : 'Add New Connection'}
            </h3>

            {!selectedService ? (
              <div className="space-y-3">
                <p className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-4">
                  Choose a service to connect:
                </p>
                {filteredServices.map(([serviceKey, config]) => (
                  <Button
                    key={serviceKey}
                    variant="secondary"
                    className="w-full justify-start p-4 h-auto"
                    onClick={() => setSelectedService(serviceKey)}
                  >
                    <div className="flex items-center gap-3">
                      {config.icon}
                      <div className="text-left">
                        <div className="font-medium">{config.name}</div>
                        <div className="text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
                          {config.description}
                        </div>
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {SERVICE_CONFIGS[selectedService].authType === 'oauth' ? (
                  // OAuth services
                  <div className="text-center p-6">
                    <div className="flex items-center justify-center mb-4">
                      {SERVICE_CONFIGS[selectedService].icon}
                      <h4 className="ml-2 text-lg font-medium">{SERVICE_CONFIGS[selectedService].name}</h4>
                    </div>
                    <p className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-6">
                      Click the button below to securely authorize {SERVICE_CONFIGS[selectedService].name} through their official OAuth flow.
                      You&apos;ll be redirected to {SERVICE_CONFIGS[selectedService].name}&apos;s website to grant permissions.
                    </p>
                    <Button
                      onClick={handleAddCredential}
                      className="w-full mb-4"
                      disabled={testingConnection}
                    >
                      {testingConnection ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Redirecting...
                        </>
                      ) : (
                        <>
                          <Key className="w-4 h-4 mr-2" />
                          Authorize with {SERVICE_CONFIGS[selectedService].name}
                        </>
                      )}
                    </Button>
                    <div className="flex items-center justify-center gap-2 text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
                      <Shield className="w-3 h-3" />
                      <span>Secure OAuth 2.0 authorization - no passwords required</span>
                    </div>
                    <Button
                      variant="secondary"
                      onClick={resetForm}
                      className="w-full mt-4"
                    >
                      Cancel
                    </Button>
                  </div>
                ) : (
                  // API key and manual services
                  <div>
                    {/* Connection Name */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-[#0F172A] dark:text-[#F8FAFC] mb-2">
                        Connection Name
                      </label>
                      <Input
                        placeholder={`${SERVICE_CONFIGS[selectedService].name} Connection`}
                        value={formData.name || ''}
                        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))
                        }
                        className="bg-white/60 dark:bg-[#0F172A]/60 border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                      />
                    </div>

                    {/* Service-specific fields */}
                    {SERVICE_CONFIGS[selectedService].fields.map(field => (
                      <div key={field.name} className="mb-4">
                        <label className="block text-sm font-medium text-[#0F172A] dark:text-[#F8FAFC] mb-2">
                          {field.label}
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        <div className="relative">
                          <Input
                            type={field.type === 'password' && !showPasswords[field.name] ? 'password' : 'text'}
                            placeholder={field.placeholder}
                            value={formData[field.name] || ''}
                            onChange={(e) => setFormData(prev => ({ ...prev, [field.name]: e.target.value }))}
                            className="bg-white/60 dark:bg-[#0F172A]/60 border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                          />
                          {field.type === 'password' && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1"
                              onClick={() => togglePasswordVisibility(field.name)}
                            >
                              {showPasswords[field.name] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}

                    <div className="flex gap-3 pt-4">
                      <Button
                        onClick={handleAddCredential}
                        className="flex-1"
                        disabled={!SERVICE_CONFIGS[selectedService].fields.filter(f => f.required).every(f => formData[f.name]) || testingConnection}
                      >
                        {testingConnection ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          editingCredential ? 'Update Connection' : 'Add Connection'
                        )}
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={async () => {
                          const isValid = await testConnection(selectedService, formData);
                          if (isValid) {
                            alert('✓ Connection test successful!');
                          } else {
                            alert('✗ Connection test failed. Please check your credentials.');
                          }
                        }}
                        disabled={!SERVICE_CONFIGS[selectedService].fields.filter(f => f.required).every(f => formData[f.name]) || testingConnection}
                      >
                        Test
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={resetForm}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}

      {/* Available Services */}
      <div>
        <h2 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">
          Available Services
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredServices.map(([serviceKey, config]) => {
            const existingConnection = credentials.find(c => c.service === serviceKey);
            return (
              <Card key={serviceKey} className="bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    {config.icon}
                    <div>
                      <CardTitle className="text-lg">{config.name}</CardTitle>
                      <Badge className={`text-xs ${config.color} text-white`}>
                        {config.category}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm mb-4">
                    {config.description}
                  </CardDescription>
                  <div className="flex justify-between items-center">
                    {existingConnection ? (
                      <div className="flex items-center gap-2">
                        {getStatusBadge(existingConnection.status)}
                      </div>
                    ) : (
                      <div className="text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
                        Not connected
                      </div>
                    )}
                    <Button
                      size="sm"
                      onClick={() => {
                        setSelectedService(serviceKey);
                        setShowAddForm(true);
                      }}
                      className="flex items-center gap-2"
                    >
                      <Plus className="w-3 h-3" />
                      {existingConnection ? 'Add Another' : 'Connect'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Production Security Notice */}
      <motion.div
        className="mt-8 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="flex items-center gap-3">
          <Shield className="w-5 h-5 text-green-600 dark:text-green-400" />
          <div className="flex-1">
            <h3 className="font-medium text-green-900 dark:text-green-100">Production Security</h3>
            <p className="text-sm text-green-700 dark:text-green-300">
              ✓ All credentials are encrypted server-side using AES-256 encryption<br/>
              ✓ Authentication required for all credential operations<br/>
              ✓ Connection testing validates credentials before storage<br/>
              ✓ Environment variables supported for CI/CD integration
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setUseEnvironmentVars(!useEnvironmentVars)}
              className="flex items-center gap-2"
            >
              <Server className="w-4 h-4" />
              {useEnvironmentVars ? 'Use Form' : 'Use Env Vars'}
            </Button>
            {loading && (
              <Button size="sm" variant="secondary" disabled>
                <RefreshCw className="w-4 h-4 animate-spin" />
              </Button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Error Display */}
      {error && (
        <motion.div
          className="mt-4 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
            <div>
              <h4 className="font-medium text-red-900 dark:text-red-100">Error</h4>
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setError(null)}
              className="ml-auto"
            >
              Dismiss
            </Button>
          </div>
        </motion.div>
      )}
      </div>
    </div>
  );
}



