import React, { useRef, useState } from 'react';
import { Upload, X, FileText, Image, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { Button } from './Button';
import { Alert } from './Alert';
import { Badge } from './Badge';

/**
 * FileUpload Component - Upload de arquivos com validação e preview
 * @param {string} accept - Tipos aceitos (ex: '.pdf,.png,.jpg')
 * @param {number} maxSize - Tamanho máximo em MB
 * @param {function} onUpload - Callback ao fazer upload
 * @param {boolean} multiple - Permite múltiplos arquivos
 * @param {string} variant - Variante (default, compact)
 */
export const FileUpload = ({
  accept = '.pdf,.png,.jpg',
  maxSize = 10,
  onUpload = () => {},
  multiple = true,
  variant = 'default',
  disabled = false,
  label = 'Upload de Comprovante',
  description = 'Selecione PDF ou PNG (máx 10MB)'
}) => {
  const fileInputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    processFiles(selectedFiles);
  };

  const processFiles = (fileArray) => {
    setError(null);
    setSuccess(null);

    if (!multiple && fileArray.length > 1) {
      setError('Apenas um arquivo permitido');
      return;
    }

    const newFiles = [];
    for (const file of fileArray) {
      // Validar tamanho
      if (file.size > maxSize * 1024 * 1024) {
        setError(`Arquivo ${file.name} muito grande (máx ${maxSize}MB)`);
        continue;
      }

      // Validar tipo
      const ext = file.name.split('.').pop().toLowerCase();
      const allowedExts = accept.replace(/\./g, '').split(',');
      if (!allowedExts.includes(ext)) {
        setError(`Tipo ${ext} não permitido`);
        continue;
      }

      newFiles.push({
        file,
        id: Math.random().toString(36).substr(2, 9),
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
        isDuplicate: false,
      });
    }

    if (newFiles.length > 0) {
      if (!multiple) {
        setFiles(newFiles);
      } else {
        setFiles(prev => [...prev, ...newFiles]);
      }
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (id) => {
    setFiles(prev => prev.filter(f => f.id !== id));
    setError(null);
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      let successCount = 0;
      let failedFiles = [];
      
      for (const fileObj of files) {
        try {
          const result = await onUpload(fileObj.file);
          
          if (result?.is_duplicate) {
            setFiles(prev =>
              prev.map(f =>
                f.id === fileObj.id ? { ...f, isDuplicate: true } : f
              )
            );
          }
          
          successCount++;
        } catch (fileErr) {
          failedFiles.push({
            name: fileObj.file.name,
            error: fileErr.response?.data?.detail || fileErr.message || 'Erro desconhecido'
          });
        }
      }

      if (failedFiles.length > 0) {
        const failedList = failedFiles.map(f => `❌ ${f.name}: ${f.error}`).join('\n');
        setError(`${successCount}/${files.length} enviados.\n\nFalharam:\n${failedList}`);
      } else {
        setSuccess(`✅ ${successCount} arquivo(s) enviado(s) com sucesso!`);
        setTimeout(() => setFiles([]), 1500);
      }
    } catch (err) {
      setError(err.message || 'Erro ao enviar arquivo');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (file) => {
    if (file.type === 'application/pdf') {
      return <FileText className="w-6 h-6 text-red-500" />;
    }
    if (file.type.startsWith('image/')) {
      return <Image className="w-6 h-6 text-blue-500" />;
    }
    return <Upload className="w-6 h-6 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className={`w-full ${variant === 'compact' ? 'space-y-2' : 'space-y-4'}`}>
      {/* Label */}
      {label && <label className="block text-sm font-medium text-gray-900">{label}</label>}

      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center transition
          ${disabled ? 'bg-gray-50 border-gray-200 cursor-not-allowed' : 'border-blue-300 hover:border-blue-500 bg-blue-50 cursor-pointer'}
        `}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <Upload className={`w-8 h-8 mx-auto mb-2 ${disabled ? 'text-gray-400' : 'text-blue-500'}`} />
        <p className={`font-medium ${disabled ? 'text-gray-500' : 'text-gray-900'}`}>
          Arrastar arquivo aqui ou clicar
        </p>
        <p className="text-sm text-gray-600">{description}</p>
      </div>

      {/* Input Hidden */}
      <input
        ref={fileInputRef}
        type="file"
        multiple={multiple}
        accept={accept}
        onChange={handleFileChange}
        disabled={disabled}
        className="hidden"
      />

      {/* Error */}
      {error && <Alert variant="danger">{error}</Alert>}

      {/* Success */}
      {success && <Alert variant="success">{success}</Alert>}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2 bg-gray-50 rounded-lg p-4">
          {files.map(fileObj => (
            <div
              key={fileObj.id}
              className="flex items-center justify-between p-3 bg-white rounded border border-gray-200 hover:border-gray-300 transition"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                {fileObj.preview ? (
                  <img
                    src={fileObj.preview}
                    alt={fileObj.file.name}
                    className="w-10 h-10 object-cover rounded"
                  />
                ) : (
                  getFileIcon(fileObj.file)
                )}

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {fileObj.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(fileObj.file.size)}
                  </p>
                </div>
              </div>

              {/* Status */}
              <div className="flex items-center gap-2 ml-2">
                {fileObj.isDuplicate && (
                  <Badge variant="warning">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Duplicado
                  </Badge>
                )}

                {!loading && (
                  <button
                    onClick={() => removeFile(fileObj.id)}
                    disabled={loading}
                    className="p-1 hover:bg-red-50 rounded text-red-500 transition"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}

          {/* Upload Button */}
          {files.length > 0 && (
            <Button
              onClick={uploadFiles}
              isLoading={loading}
              disabled={loading}
              variant="primary"
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Enviando...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Enviar ({files.length})
                </>
              )}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
