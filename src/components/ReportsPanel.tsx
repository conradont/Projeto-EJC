import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { participantsApi, pdfApi } from '@/lib/api'
import { downloadBlob } from '@/lib/utils'

export default function ReportsPanel() {
  const [selectedParticipantId, setSelectedParticipantId] = useState<number | null>(null)

  const { data: participants = [] } = useQuery({
    queryKey: ['participants'],
    queryFn: () => participantsApi.getAll({ limit: 1000 }),
  })

  const handleGenerateIndividualPDF = async () => {
    if (!selectedParticipantId) {
      toast.error('Selecione um participante')
      return
    }

    try {
      const blob = await pdfApi.generateIndividual(selectedParticipantId)
      const participant = participants.find((p) => p.id === selectedParticipantId)
      const filename = `ficha_${participant?.name.replace(' ', '_') || 'participante'}.pdf`
      downloadBlob(blob, filename)
      toast.success('PDF gerado com sucesso!')
    } catch (error) {
      toast.error('Erro ao gerar PDF')
    }
  }

  const handleGenerateCompletePDF = async () => {
    try {
      const blob = await pdfApi.generateComplete()
      downloadBlob(blob, 'fichas_completas.pdf')
      toast.success('PDF completo gerado com sucesso!')
    } catch (error) {
      toast.error('Erro ao gerar PDF completo')
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">PDF Individual</h3>
        <div className="space-y-4">
          <select
            value={selectedParticipantId || ''}
            onChange={(e) => setSelectedParticipantId(Number(e.target.value) || null)}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Selecione um participante</option>
            {participants.map((participant) => (
              <option key={participant.id} value={participant.id}>
                {participant.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleGenerateIndividualPDF}
            disabled={!selectedParticipantId}
            className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Gerar PDF Individual
          </button>
        </div>
      </div>

      <div className="border-t border-gray-700 pt-6">
        <h3 className="text-xl font-semibold text-white mb-4">PDF Completo</h3>
        <button
          onClick={handleGenerateCompletePDF}
          disabled={participants.length === 0}
          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Gerar PDF Completo ({participants.length} participantes)
        </button>
      </div>
    </div>
  )
}
