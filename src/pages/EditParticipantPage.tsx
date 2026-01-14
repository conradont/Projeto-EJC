import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { participantsApi } from '@/lib/api'
import ParticipantEditForm from '@/components/ParticipantEditForm'

export default function EditParticipantPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const participantId = id ? parseInt(id, 10) : null

  const { data: participant, isLoading, error } = useQuery({
    queryKey: ['participant', participantId],
    queryFn: () => participantsApi.getById(participantId!),
    enabled: !!participantId,
  })

  if (!participantId) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-800 rounded-xl p-6 border border-red-700">
          <p className="text-white">ID do participante inválido</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-white">Carregando participante...</p>
        </div>
      </div>
    )
  }

  if (error || !participant) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-800 rounded-xl p-6 border border-red-700">
          <p className="text-white">Erro ao carregar participante ou participante não encontrado</p>
          <button
            onClick={() => navigate('/participants')}
            className="mt-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
          >
            Voltar para lista
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-white mb-8">Editar Participante</h2>
      <ParticipantEditForm participant={participant} />
    </div>
  )
}
