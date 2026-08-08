import React, { useState } from 'react';
import { apiClient } from '../services/apiClient';
import { useNotification } from '../contexts/NotificationContext';

export interface FileUploadWidgetProps {
  patientId: string;
  onUploadSuccess?: () => void;
}

export const FileUploadWidget: React.FC<FileUploadWidgetProps> = ({ patientId, onUploadSuccess }) => {
  const { showToast } = useNotification();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileCategory, setFileCategory] = useState<string>('voice');
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadProgress(0);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      showToast('warning', 'No File Selected', 'Please select a file before submitting.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(10);

    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('file_category', fileCategory);
    formData.append('file', selectedFile);

    try {
      await apiClient.post('/uploads', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          }
        },
      });

      showToast('success', 'Upload Complete', `Successfully uploaded ${selectedFile.name}`);
      setSelectedFile(null);
      setUploadProgress(0);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'Upload failed.';
      showToast('error', 'Upload Error', msg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 className="text-base font-bold text-slate-900 mb-1">Multimodal Biomarker File Upload</h3>
      <p className="text-xs text-slate-500 mb-4">Support for voice recordings, video sessions, skin images, and PDF lab records</p>

      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">File Category</label>
          <select
            value={fileCategory}
            onChange={(e) => setFileCategory(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-slate-50 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            <option value="voice">Voice Biomarker (.wav, .mp3, .m4a)</option>
            <option value="video">Video & Facial Biomarker (.mp4, .webm)</option>
            <option value="image">Lesion / Clinical Image (.jpg, .png)</option>
            <option value="pdf_report">PDF Lab & Clinical Report (.pdf)</option>
          </select>
        </div>

        <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-indigo-400 transition-colors bg-slate-50">
          <input
            type="file"
            onChange={handleFileChange}
            id="file-input"
            className="hidden"
            disabled={isUploading}
          />
          <label htmlFor="file-input" className="cursor-pointer flex flex-col items-center">
            <span className="text-xs font-semibold text-indigo-600 mb-1">
              {selectedFile ? selectedFile.name : 'Click to select or drag & drop file'}
            </span>
            <span className="text-[10px] text-slate-400">Maximum file size: 50MB</span>
          </label>
        </div>

        {isUploading && (
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-indigo-600 h-2 transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        )}

        <button
          type="submit"
          disabled={!selectedFile || isUploading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs py-2.5 rounded-lg shadow-sm disabled:opacity-50 transition-colors"
        >
          {isUploading ? `Uploading (${uploadProgress}%)...` : 'Upload Asset'}
        </button>
      </form>
    </div>
  );
};