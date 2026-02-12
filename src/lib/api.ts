import axios from 'axios'
import type { Participant, ParticipantCreate, ParticipantUpdate } from '@/types/participant'

/** Base URL da API: use VITE_API_BASE_URL para Supabase Edge Functions ou outro host; senão /api (proxy local/Vercel). */
const getApiBaseUrl = () => (import.meta.env.VITE_API_BASE_URL as string) ?? '/api'

const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ParticipantsListResponse {
  participants: Participant[]
  total: number
}

export const participantsApi = {
  getAll: async (params?: { skip?: number; limit?: number; search?: string }): Promise<ParticipantsListResponse> => {
    const response = await api.get<ParticipantsListResponse>('/participants', { params })
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
    const base = getApiBaseUrl()
    const response = await axios.post<{ filename: string; path: string; url?: string }>(
      `${base}/photos/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /** Retorna a URL da foto: se path já for URL (Supabase), devolve como está; senão base da API + /photos/{path}. */
  getUrl: (filename: string | null | undefined): string | null => {
    if (!filename) return null
    if (filename.startsWith('http://') || filename.startsWith('https://')) return filename
    return `${getApiBaseUrl()}/photos/${filename}`
  },
}

export const logoApi = {
  upload: async (file: File): Promise<{ filename: string; path: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    const base = getApiBaseUrl()
    const response = await axios.post<{ filename: string; path: string }>(
      `${base}/logo/upload`,
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
    return `${getApiBaseUrl()}/logo`
  },

  delete: async (): Promise<void> => {
    await axios.delete(`${getApiBaseUrl()}/logo`)
  },
}

export default api
