import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useNavigate } from 'react-router-dom'
import { participantSchema, type ParticipantFormData } from '@/schemas/participant'
import { participantsApi } from '@/lib/api'
import type { Participant } from '@/types/participant'
import { formatDateToBrazilian } from '@/lib/masks'
import FormField from './FormField'
import MaskedInput from './MaskedInput'
import SacramentsSection from './SacramentsSection'
import ChurchMovementSection from './ChurchMovementSection'
import FamilySection from './FamilySection'
import ECCSection from './ECCSection'
import RestrictionsSection from './RestrictionsSection'
import PhotoUpload from './PhotoUpload'

interface ParticipantEditFormProps {
  participant: Participant
}

export default function ParticipantEditForm({ participant }: ParticipantEditFormProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    control,
    formState: { errors, isSubmitting },
  } = useForm<ParticipantFormData>({
    resolver: zodResolver(participantSchema),
  })

  // Preencher formulário com dados do participante
  useEffect(() => {
    if (participant) {
      reset({
        name: participant.name || '',
        common_name: participant.common_name || null,
        birth_date: participant.birth_date ? formatDateToBrazilian(participant.birth_date) : null,
        instagram: participant.instagram || null,
        address: participant.address || null,
        neighborhood: participant.neighborhood || null,
        email: participant.email || null,
        phone: participant.phone || null,
        sacraments: participant.sacraments || null,
        church_movement: participant.church_movement || null,
        church_movement_info: participant.church_movement_info || null,
        father_name: participant.father_name || null,
        father_contact: participant.father_contact || null,
        mother_name: participant.mother_name || null,
        mother_contact: participant.mother_contact || null,
        ecc_participant: participant.ecc_participant ?? false,
        ecc_info: participant.ecc_info || null,
        has_restrictions: participant.has_restrictions ?? false,
        restrictions_info: participant.restrictions_info || null,
        observations: participant.observations || null,
        photo_path: participant.photo_path || null,
      })
    }
  }, [participant, reset])

  const mutation = useMutation({
    mutationFn: (data: ParticipantFormData) => participantsApi.update(participant.id, data),
    onSuccess: () => {
      toast.success('Participante atualizado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['participants'] })
      queryClient.invalidateQueries({ queryKey: ['participant', participant.id] })
      navigate('/participants')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar participante')
    },
  })

  const onSubmit = (data: ParticipantFormData) => {
    mutation.mutate(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-6">Informações Pessoais</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <FormField
            label="Nome Completo *"
            error={errors.name}
            {...register('name')}
          />
          <FormField
            label="Nome Usual"
            error={errors.common_name}
            {...register('common_name')}
          />
          <MaskedInput
            label="Data de Nascimento"
            error={errors.birth_date}
            mask="date"
            register={register('birth_date')}
            control={control}
            placeholder="DD/MM/AAAA"
          />
          <FormField
            label="Instagram"
            error={errors.instagram}
            {...register('instagram')}
            placeholder="@usuario"
          />
          <FormField
            label="Endereço"
            error={errors.address}
            {...register('address')}
          />
          <FormField
            label="Bairro / Comunidade"
            error={errors.neighborhood}
            {...register('neighborhood')}
          />
          <MaskedInput
            label="Email"
            error={errors.email}
            mask="email"
            register={register('email')}
            control={control}
            type="email"
            placeholder="exemplo@email.com"
          />
          <MaskedInput
            label="Celular"
            error={errors.phone}
            mask="phone"
            register={register('phone')}
            control={control}
            placeholder="(00) 00000-0000"
          />
        </div>
      </div>

      <SacramentsSection register={register} setValue={setValue} watch={watch} />

      <ChurchMovementSection register={register} setValue={setValue} watch={watch} />

      <FamilySection register={register} errors={errors} control={control} />

      <ECCSection register={register} setValue={setValue} watch={watch} />

      <RestrictionsSection register={register} setValue={setValue} watch={watch} />

      <PhotoUpload setValue={setValue} watch={watch} />

      <div className="flex gap-4 justify-end">
        <button
          type="button"
          onClick={() => navigate('/participants')}
          className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Salvando...' : 'Salvar Alterações'}
        </button>
      </div>
    </form>
  )
}
