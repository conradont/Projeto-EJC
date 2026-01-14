import { UseFormRegister, UseFormSetValue, UseFormWatch } from 'react-hook-form'
import { ParticipantFormData } from '@/schemas/participant'
import { useEffect } from 'react'

interface SacramentsSectionProps {
  register: UseFormRegister<ParticipantFormData>
  setValue: UseFormSetValue<ParticipantFormData>
  watch: UseFormWatch<ParticipantFormData>
}

const sacraments = ['Batismo', 'Primeira Eucaristia', 'Crisma'] as const
const statuses = ['Concluído', 'Não Concluído', 'Em Processo'] as const

export default function SacramentsSection({ setValue, watch }: SacramentsSectionProps) {
  const currentSacraments = watch('sacraments') || ''

  // Parse dos sacramentos para obter o status de cada um
  const getSacramentStatus = (sacrament: string): string => {
    const sacramentsArray = currentSacraments.split(',').filter(Boolean)
    const found = sacramentsArray.find((s) => s.startsWith(`${sacrament}:`))
    return found ? found.split(':')[1] : 'Não Informado'
  }

  const handleSacramentChange = (
    sacrament: string,
    status: string
  ) => {
    const sacramentsArray = currentSacraments
      .split(',')
      .filter((s) => s && !s.startsWith(`${sacrament}:`))
    
    if (status !== 'Não Informado') {
      sacramentsArray.push(`${sacrament}:${status}`)
    }
    
    setValue('sacraments', sacramentsArray.join(','))
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Sacramentos</h3>
      <div className="space-y-4">
        {sacraments.map((sacrament) => (
          <div key={sacrament}>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {sacrament}
            </label>
            <div className="flex gap-4">
              {statuses.map((status) => (
                <label key={status} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name={`sacrament_${sacrament}`}
                    value={status}
                    checked={getSacramentStatus(sacrament) === status}
                    onChange={() => handleSacramentChange(sacrament, status)}
                    className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
                  />
                  <span className="text-gray-300">{status}</span>
                </label>
              ))}
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={`sacrament_${sacrament}`}
                  value="Não Informado"
                  checked={getSacramentStatus(sacrament) === 'Não Informado'}
                  onChange={() => handleSacramentChange(sacrament, 'Não Informado')}
                  className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
                />
                <span className="text-gray-300">Não Informado</span>
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
