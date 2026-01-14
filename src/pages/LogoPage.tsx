import { useState, useEffect } from 'react'
import { logoApi } from '@/lib/api'
import { toast } from 'sonner'

export default function LogoPage() {
  const [logoUrl, setLogoUrl] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadLogo()
  }, [])

  const loadLogo = async () => {
    try {
      setLoading(true)
      const url = logoApi.getUrl()
      // Verificar se a logo existe fazendo uma requisição
      try {
        const response = await fetch(url)
        if (response.ok) {
          setLogoUrl(url)
        } else {
          setLogoUrl(null)
        }
      } catch {
        setLogoUrl(null)
      }
    } catch (error) {
      console.error('Erro ao carregar logo:', error)
      setLogoUrl(null)
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploading(true)
      
      try {
        // Criar preview local imediatamente
        const reader = new FileReader()
        reader.onloadend = () => {
          setLogoUrl(reader.result as string)
        }
        reader.readAsDataURL(file)
        
        // Fazer upload para o servidor
        await logoApi.upload(file)
        
        // Recarregar logo do servidor
        await loadLogo()
        
        toast.success('Logo enviada com sucesso!')
      } catch (error) {
        console.error('Erro ao fazer upload da logo:', error)
        setLogoUrl(null)
        toast.error('Erro ao fazer upload da logo. Tente novamente.')
      } finally {
        setUploading(false)
      }
    }
  }

  const handleDelete = async () => {
    if (!confirm('Tem certeza que deseja remover a logo?')) {
      return
    }

    try {
      await logoApi.delete()
      setLogoUrl(null)
      toast.success('Logo removida com sucesso!')
    } catch (error) {
      console.error('Erro ao remover logo:', error)
      toast.error('Erro ao remover logo. Tente novamente.')
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-2xl font-semibold text-white mb-6">Logo do Evento</h2>
        
        <div className="space-y-6">
          <div>
            <p className="text-gray-300 mb-4">
              A logo do evento aparecerá no cabeçalho dos PDFs gerados, posicionada à direita.
            </p>
            <p className="text-sm text-gray-400 mb-6">
              Formatos suportados: PNG, JPG, JPEG, GIF, WEBP, SVG
            </p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-400">Carregando...</div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              {logoUrl ? (
                <>
                  <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                    <img
                      src={logoUrl}
                      alt="Logo do evento"
                      className="max-w-xs max-h-48 object-contain"
                    />
                  </div>
                  <div className="flex gap-4">
                    <label className="cursor-pointer">
                      <span className={`px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors inline-block ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                        {uploading ? 'Enviando...' : 'Alterar Logo'}
                      </span>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        disabled={uploading}
                        className="hidden"
                      />
                    </label>
                    <button
                      onClick={handleDelete}
                      disabled={uploading}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Remover Logo
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="w-64 h-48 border-2 border-dashed border-gray-600 rounded-lg flex items-center justify-center bg-gray-900">
                    <span className="text-gray-500 text-sm">Nenhuma logo cadastrada</span>
                  </div>
                  <label className="cursor-pointer">
                    <span className={`px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors inline-block ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                      {uploading ? 'Enviando...' : 'Selecionar Logo'}
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      disabled={uploading}
                      className="hidden"
                    />
                  </label>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
