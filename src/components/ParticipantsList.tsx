import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { participantsApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import ParticipantCard from './ParticipantCard'
import SearchBar from './SearchBar'
import FiltersPanel from './FiltersPanel'

export default function ParticipantsList() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const itemsPerPage = 10

  const { data: participants = [], isLoading } = useQuery({
    queryKey: ['participants', search],
    queryFn: () =>
      participantsApi.getAll({
        skip: (page - 1) * itemsPerPage,
        limit: itemsPerPage,
        search: search || undefined,
      }),
  })

  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: participantsApi.delete,
    onSuccess: () => {
      toast.success('Participante excluído com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['participants'] })
    },
    onError: () => {
      toast.error('Erro ao excluir participante')
    },
  })

  const handleDelete = (id: number) => {
    if (confirm('Tem certeza que deseja excluir este participante?')) {
      deleteMutation.mutate(id)
    }
  }

  if (isLoading) {
    return <div className="text-center text-gray-400">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <SearchBar value={search} onChange={setSearch} />
      <FiltersPanel />
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {participants.map((participant) => (
          <ParticipantCard
            key={participant.id}
            participant={participant}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {participants.length === 0 && (
        <div className="text-center text-gray-400 py-12">
          Nenhum participante encontrado
        </div>
      )}

      <div className="flex justify-center gap-2">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-4 py-2 bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
        >
          Anterior
        </button>
        <span className="px-4 py-2 text-gray-300">Página {page}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={participants.length < itemsPerPage}
          className="px-4 py-2 bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
        >
          Próxima
        </button>
      </div>
    </div>
  )
}
