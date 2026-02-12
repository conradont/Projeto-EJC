import axios from 'axios'
import type { Participant, ParticipantCreate, ParticipantUpdate } from '@/types/participant'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const participantsApi = {
  getAll: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const response = await api.get<Participant[]>('/participants', { params })
    return response.data
  },

  getById: async (id: number) => {
    const response = await api.get<Participant>(`/participants/${id}`)
    return response.data
  },

  create: async (data: ParticipantCreate) => {
    const response = await api.post<Participant>('/participants', data)
    return response.data
  },

  update: async (id: number, data: ParticipantUpdate) => {
    const response = await api.put<Participant>(`/participants/${id}`, data)
    return response.data
  },

  delete: async (id: number) => {
    await api.delete(`/participants/${id}`)
  },
}

export const pdfApi = {
  generateIndividual: async (participantId: number) => {
    const response = await api.get(`/pdf/participant/${participantId}`, {
      responseType: 'blob',
    })
    return response.data
  },

  generateComplete: async () => {
    const response = await api.get('/pdf/complete', {
      responseType: 'blob',
    })
    return response.data
  },
}

export const photosApi = {
  upload: async (file: File): Promise<{ filename: string; path: string; url?: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post<{ filename: string; path: string; url?: string }>(
      '/api/photos/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /** Retorna a URL da foto: se path já for URL (Supabase), devolve como está; senão /api/photos/{path}. */
  getUrl: (filename: string | null | undefined): string | null => {
    if (!filename) return null
    if (filename.startsWith('http://') || filename.startsWith('https://')) return filename
    return `/api/photos/${filename}`
  },
}

export const logoApi = {
  upload: async (file: File): Promise<{ filename: string; path: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post<{ filename: string; path: string }>(
      '/api/logo/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  getUrl: (): string => {
    return '/api/logo'
  },

  delete: async (): Promise<void> => {
    await axios.delete('/api/logo')
  },
}

export default api
