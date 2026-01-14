import { Participant } from '@/types/participant'
import { formatDate, formatPhone } from '@/lib/utils'
import { Link } from 'react-router-dom'

interface ParticipantCardProps {
  participant: Participant
  onDelete: (id: number) => void
}

export default function ParticipantCard({ participant, onDelete }: ParticipantCardProps) {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-primary-500 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-white">{participant.name}</h3>
          {participant.common_name && (
            <p className="text-gray-400 text-sm">{participant.common_name}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Link
            to={`/participants/${participant.id}/edit`}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            Editar
          </Link>
          <button
            onClick={() => onDelete(participant.id)}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            Excluir
          </button>
        </div>
      </div>
      
      <div className="space-y-2 text-sm">
        {participant.birth_date && (
          <p className="text-gray-400">
            <span className="text-gray-500">Nascimento:</span> {formatDate(participant.birth_date)}
          </p>
        )}
        {participant.email && (
          <p className="text-gray-400">
            <span className="text-gray-500">Email:</span> {participant.email}
          </p>
        )}
        {participant.phone && (
          <p className="text-gray-400">
            <span className="text-gray-500">Telefone:</span> {formatPhone(participant.phone)}
          </p>
        )}
        {participant.instagram && (
          <p className="text-gray-400">
            <span className="text-gray-500">Instagram:</span> {participant.instagram}
          </p>
        )}
      </div>
    </div>
  )
}
