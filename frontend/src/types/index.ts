export interface Document {
  id: string;
  name: string;
  doc_type: 'datasheet' | 'setup' | 'config' | 'paper' | 'journal';
  file_path: string;
  parsed_content: string | null;
  chunk_count: number;
  file_size: number;
  upload_date: string;
  collection_name: string;
}

export interface DataFile {
  id: string;
  name: string;
  file_path: string;
  file_size: number;
  description: string | null;
  upload_date: string;
}

export interface Experiment {
  id: string;
  paper_id: string;
  data_file_ids: string;
  user_instructions: string | null;
  status: 'pending' | 'running' | 'completed' | 'failed';
  generated_code: string | null;
  execution_output: string | null;
  execution_error: string | null;
  result_files: string | null;
  iteration_count: number;
  created_at: string;
  completed_at: string | null;
}

export interface SearchResult {
  chunk_text: string;
  metadata: Record<string, any>;
  score: number;
}

export interface WSMessage {
  status: string;
  message: string;
  data?: any;
}
