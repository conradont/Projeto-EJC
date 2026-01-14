import { UseFormRegister, FieldErrors, Control } from 'react-hook-form'
import { ParticipantFormData } from '@/schemas/participant'
import FormField from './FormField'
import MaskedInput from './MaskedInput'

interface FamilySectionProps {
  register: UseFormRegister<ParticipantFormData>
  errors: FieldErrors<ParticipantFormData>
  control?: Control<ParticipantFormData>
}

export default function FamilySection({ register, errors, control }: FamilySectionProps) {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-6">Informações Familiares</h3>
      <div className="grid md:grid-cols-2 gap-4">
        <FormField
          label="Nome do Pai"
          error={errors.father_name}
          {...register('father_name')}
        />
        <MaskedInput
          label="Contato do Pai"
          error={errors.father_contact}
          mask="phone"
          register={register('father_contact')}
          control={control}
          placeholder="(00) 00000-0000"
        />
        <FormField
          label="Nome da Mãe"
          error={errors.mother_name}
          {...register('mother_name')}
        />
        <MaskedInput
          label="Contato da Mãe"
          error={errors.mother_contact}
          mask="phone"
          register={register('mother_contact')}
          control={control}
          placeholder="(00) 00000-0000"
        />
      </div>
    </div>
  )
}
