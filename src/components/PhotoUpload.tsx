import { UseFormSetValue, UseFormWatch } from 'react-hook-form'
import { ParticipantFormData } from '@/schemas/participant'
import { useState, useEffect } from 'react'
import { photosApi } from '@/lib/api'

interface PhotoUploadProps {
  setValue: UseFormSetValue<ParticipantFormData>
  watch?: UseFormWatch<ParticipantFormData>
}

export default function PhotoUpload({ setValue, watch }: PhotoUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const photoPath = watch?.('photo_path')
  
  // Carregar foto existente se houver
  useEffect(() => {
    if (photoPath && !preview) {
      const photoUrl = photosApi.getUrl(photoPath)
      if (photoUrl) {
        setPreview(photoUrl)
      }
    }
  }, [photoPath, preview])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploading(true)
      
      try {
        // Criar preview local imediatamente
        const reader = new FileReader()
        reader.onloadend = () => {
          setPreview(reader.result as string)
        }
        reader.readAsDataURL(file)
        
        // Fazer upload para o servidor
        const result = await photosApi.upload(file)
        // path = caminho no Storage (Supabase) ou filename (local); a API gera signed URL ao servir
        setValue('photo_path', result.path ?? result.filename)
      } catch (error) {
        console.error('Erro ao fazer upload da foto:', error)
        setPreview(null)
        setValue('photo_path', null)
        alert('Erro ao fazer upload da foto. Tente novamente.')
      } finally {
        setUploading(false)
      }
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Foto do Participante</h3>
      <div className="flex flex-col items-center gap-4">
        {preview ? (
          <img
            src={preview}
            alt="Preview"
            className="w-32 h-32 object-cover rounded-lg border-2 border-gray-600"
          />
        ) : (
          <div className="w-32 h-32 border-2 border-dashed border-gray-600 rounded-lg flex items-center justify-center">
            <span className="text-gray-500 text-sm">Sem foto</span>
          </div>
        )}
        <label className="cursor-pointer">
          <span className={`px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors inline-block ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
            {uploading ? 'Enviando...' : 'Selecionar Foto'}
          </span>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>
    </div>
  )
}
