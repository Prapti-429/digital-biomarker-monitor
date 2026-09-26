import React, { useState } from 'react';
import { apiClient } from '../services/apiClient';
import { useNotification } from '../contexts/NotificationContext';

export interface FileUploadWidgetProps { patientId: string; onUploadSuccess?: () => void; }

type UploadResult = { filename?: string; processing_status?: string; notes?: string };

export const FileUploadWidget: React.FC<FileUploadWidgetProps> = ({ patientId, onUploadSuccess }) => {
  const { showToast } = useNotification();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileCategory, setFileCategory] = useState('voice');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const next = e.target.files?.[0];
    if (next) { setSelectedFile(next); setUploadProgress(0); setAnalysis(null); }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) { showToast('warning', 'No File Selected', 'Please select a file before submitting.'); return; }
    setIsUploading(true); setUploadProgress(10); setAnalysis(null);
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('file_category', fileCategory);
    formData.append('file', selectedFile);
    try {
      const response = await apiClient.post<UploadResult>('/uploads', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => { if (event.total) setUploadProgress(Math.round((event.loaded * 100) / event.total)); },
      });
      let parsed: Record<string, unknown> | null = null;
      if (response.data?.notes) {
        try { parsed = JSON.parse(response.data.notes); } catch { parsed = null; }
      }
      setAnalysis((parsed?.analysis as Record<string, unknown>) || null);
      showToast('success', 'Upload analyzed', `Extracted data from ${selectedFile.name}`);
      setSelectedFile(null); setUploadProgress(100);
      onUploadSuccess?.();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'Upload failed.';
      showToast('error', 'Upload Error', msg);
    } finally { setIsUploading(false); }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 className="text-base font-bold text-slate-900 mb-1">Multimodal File Upload</h3>
      <p className="text-xs text-slate-500 mb-4">Upload a voice sample, video, image, or PDF. NUVYRA will extract available technical data and show what was found.</p>
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">File Category</label>
          <select value={fileCategory} onChange={(e) => setFileCategory(e.target.value)} className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-slate-50">
            <option value="voice">Voice Biomarker (.wav, .mp3, .m4a)</option>
            <option value="video">Video & Facial Biomarker (.mp4, .webm)</option>
            <option value="image">Image (.jpg, .png)</option>
            <option value="pdf_report">PDF Report (.pdf)</option>
          </select>
        </div>
        <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center bg-slate-50">
          <input type="file" onChange={handleFileChange} id="file-input" className="hidden" disabled={isUploading} />
          <label htmlFor="file-input" className="cursor-pointer flex flex-col items-center">
            <span className="text-xs font-semibold text-indigo-600 mb-1">{selectedFile ? selectedFile.name : 'Click to select or drag & drop file'}</span>
            <span className="text-[10px] text-slate-400">Maximum file size: 50MB</span>
          </label>
        </div>
        {isUploading && <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden"><div className="bg-indigo-600 h-2 transition-all" style={{ width: `${uploadProgress}%` }} /></div>}
        <button type="submit" disabled={!selectedFile || isUploading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs py-2.5 rounded-lg disabled:opacity-50">{isUploading ? `Processing (${uploadProgress}%)...` : 'Upload & Analyze'}</button>
      </form>
      {analysis && <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-xs text-slate-700">
        <div className="font-semibold text-emerald-800 mb-2">Extracted data</div>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(analysis).filter(([key]) => key !== 'text_preview').map(([key, value]) => <div key={key} className="rounded-lg bg-white/70 p-2"><div className="text-slate-500">{key.replace(/_/g, ' ')}</div><div className="font-medium break-words">{typeof value === 'object' ? JSON.stringify(value) : String(value)}</div></div>)}
        </div>
        {typeof analysis.text_preview === 'string' && analysis.text_preview && <div className="mt-3"><div className="text-slate-500 mb-1">Extracted text preview</div><pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-white p-3 text-[11px]">{analysis.text_preview}</pre></div>}
      </div>}
    </div>
  );
};
