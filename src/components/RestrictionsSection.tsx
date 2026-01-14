import { UseFormRegister, UseFormSetValue, UseFormWatch } from 'react-hook-form'
import { ParticipantFormData } from '@/schemas/participant'
import TextAreaField from './TextAreaField'

interface RestrictionsSectionProps {
  register: UseFormRegister<ParticipantFormData>
  setValue: UseFormSetValue<ParticipantFormData>
  watch: UseFormWatch<ParticipantFormData>
}

export default function RestrictionsSection({
  register,
  setValue,
  watch,
}: RestrictionsSectionProps) {
  const hasRestrictions = watch('has_restrictions') === true

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Informações Adicionais</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Possui restrições alimentares ou alergias?
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="has_restrictions"
                value="yes"
                checked={hasRestrictions}
                onChange={() => setValue('has_restrictions', true)}
                className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
              />
              <span className="text-gray-300">Sim</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="has_restrictions"
                value="no"
                checked={!hasRestrictions}
                onChange={() => {
                  setValue('has_restrictions', false)
                  setValue('restrictions_info', null)
                }}
                className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
              />
              <span className="text-gray-300">Não</span>
            </label>
          </div>
        </div>
        {hasRestrictions && (
          <TextAreaField
            label="Detalhes sobre restrições alimentares ou alergias"
            error={undefined}
            {...register('restrictions_info')}
            placeholder="Detalhes sobre restrições alimentares ou alergias"
          />
        )}
      </div>
    </div>
  )
}
