import { UseFormRegister, UseFormSetValue, UseFormWatch } from 'react-hook-form'
import { ParticipantFormData } from '@/schemas/participant'
import TextAreaField from './TextAreaField'

interface ECCSectionProps {
  register: UseFormRegister<ParticipantFormData>
  setValue: UseFormSetValue<ParticipantFormData>
  watch: UseFormWatch<ParticipantFormData>
}

export default function ECCSection({ register, setValue, watch }: ECCSectionProps) {
  const eccParticipant = watch('ecc_participant') === true

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Informações do ECC</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Pais são encontristas do ECC?
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="ecc_participant"
                value="yes"
                checked={eccParticipant}
                onChange={() => setValue('ecc_participant', true)}
                className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
              />
              <span className="text-gray-300">Sim</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="ecc_participant"
                value="no"
                checked={!eccParticipant}
                onChange={() => {
                  setValue('ecc_participant', false)
                  setValue('ecc_info', null)
                }}
                className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 focus:ring-primary-500"
              />
              <span className="text-gray-300">Não</span>
            </label>
          </div>
        </div>
        {eccParticipant && (
          <TextAreaField
            label="Informações adicionais sobre ECC"
            error={undefined}
            {...register('ecc_info')}
            placeholder="Informações adicionais sobre ECC"
          />
        )}
      </div>
    </div>
  )
}
