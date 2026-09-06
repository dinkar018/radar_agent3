import axios from 'axios';
import { Document, DataFile, Experiment, SearchResult } from '../types';

const API_URL = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Accept': 'application/json',
  },
});

export const api = {
  // Knowledge Base
  uploadDocument: (data: FormData) =>
    client.post<Document>('/kb/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data),
  listDocuments: (docType?: string) =>
    client.get<Document[]>('/kb/documents', { params: docType ? { doc_type: docType } : {} }).then(res => res.data),
  getDocument: (id: string) =>
    client.get<Document>(`/kb/documents/${id}`).then(res => res.data),
  deleteDocument: (id: string) =>
    client.delete(`/kb/documents/${id}`),
  searchKB: (query: string, collection: string = 'knowledge_base', topK: number = 10) =>
    client.post<SearchResult[]>('/kb/search', { query, collection, top_k: topK }).then(res => res.data),

  // Radar Data
  uploadDataFile: (data: FormData) =>
    client.post<DataFile>('/data/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data),
  listDataFiles: () =>
    client.get<DataFile[]>('/data/files').then(res => res.data),
  getDataFile: (id: string) =>
    client.get<DataFile>(`/data/files/${id}`).then(res => res.data),
  deleteDataFile: (id: string) =>
    client.delete(`/data/files/${id}`),

  // Experiments
  createExperiment: (data: { paper_id: string; data_file_ids: string[]; user_instructions?: string }) =>
    client.post<Experiment>('/experiments/', data).then(res => res.data),
  listExperiments: () =>
    client.get<Experiment[]>('/experiments/').then(res => res.data),
  getExperiment: (id: string) =>
    client.get<Experiment>(`/experiments/${id}`).then(res => res.data),
  deleteExperiment: (id: string) =>
    client.delete(`/experiments/${id}`),
  rerunExperiment: (id: string) =>
    client.post<Experiment>(`/experiments/${id}/rerun`).then(res => res.data),

  // Agent
  runAgent: (data: { paper_id: string; data_file_ids: string[]; user_instructions?: string }) =>
    client.post<{ experiment_id: string; status: string }>('/agent/run', data).then(res => res.data),

  // Results URL helper
  getResultUrl: (filePath: string) => `${API_URL}/results/${filePath}`,
};
