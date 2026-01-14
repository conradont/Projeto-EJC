import { UseFormRegister, UseFormSetValue, UseFormWatch } from 'react-hook-form'
import { ParticipantFormData } from '@/schemas/participant'
import FormField from './FormField'
import TextAreaField from './TextAreaField'

interface ChurchMovementSectionProps {
  register: UseFormRegister<ParticipantFormData>
  setValue: UseFormSetValue<ParticipantFormData>
  watch: UseFormWatch<ParticipantFormData>
}

export default function ChurchMovementSection({
  register,
  setValue,
  watch,
}: ChurchMovementSectionProps) {
  const churchMovement = watch('church_movement')
  // Considera "Sim" se o campo não é null e não é string vazia
  // Mas também precisa considerar quando o usuário ainda não selecionou nada
  const hasMovement = churchMovement !== null && churchMovement !== ''
  
  // Estado para controlar se "Sim" ou "Não" foi selecionado
  // Se church_movement é null, então "Não" está selecionado
  // Se church_movement não é null (mesmo que vazio), então "Sim" está selecionado
  const movementSelected = churchMovement !== null

  const handleMovementChange = (value: boolean) => {
    if (value) {
      // Quando seleciona "Sim", inicializa com string vazia para mostrar o campo
      if (churchMovement === null) {
        setValue('church_movement', '')
      }
    } else {
      // Quando seleciona "Não", limpa todos os campos relacionados
      setValue('church_movement', null)
      setValue('church_movement_info', null)
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Informações da Igreja</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Participa de algum movimento da igreja?
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="has_church_movement"
                value="yes"
                checked={movementSelected}
                onChange={() => handleMovementChange(true)}
                className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
              />
              <span className="text-gray-300">Sim</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="has_church_movement"
                value="no"
                checked={!movementSelected}
                onChange={() => handleMovementChange(false)}
                className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
              />
              <span className="text-gray-300">Não</span>
            </label>
          </div>
        </div>
        {movementSelected && (
          <div className="space-y-4">
            <FormField
              label="Nome do movimento"
              error={undefined}
              {...register('church_movement')}
              placeholder="Nome do movimento da igreja"
            />
            <TextAreaField
              label="Informações adicionais sobre o movimento"
              error={undefined}
              {...register('church_movement_info')}
              placeholder="Informações adicionais sobre participação no movimento"
            />
          </div>
        )}
      </div>
    </div>
  )
}
