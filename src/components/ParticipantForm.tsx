import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { participantSchema, type ParticipantFormData } from '@/schemas/participant'
import { participantsApi } from '@/lib/api'
import FormField from './FormField'
import MaskedInput from './MaskedInput'
import SacramentsSection from './SacramentsSection'
import ChurchMovementSection from './ChurchMovementSection'
import FamilySection from './FamilySection'
import ECCSection from './ECCSection'
import RestrictionsSection from './RestrictionsSection'
import PhotoUpload from './PhotoUpload'

const DRAFT_STORAGE_KEY = 'ejc_form_draft'

export default function ParticipantForm() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [draftChecked, setDraftChecked] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ParticipantFormData>({
    resolver: zodResolver(participantSchema),
    defaultValues: {
      ecc_participant: false,
      has_restrictions: false,
    },
  })

  useEffect(() => {
    if (draftChecked) return
    setDraftChecked(true)
    try {
      const raw = localStorage.getItem(DRAFT_STORAGE_KEY)
      if (!raw) return
      const draft = JSON.parse(raw) as ParticipantFormData
      if (draft && typeof draft === 'object' && draft.name) {
        toast.info('Há dados não enviados. Os dados foram restaurados no formulário.', { duration: 5000 })
        reset({
          ...draft,
          ecc_participant: draft.ecc_participant ?? false,
          has_restrictions: draft.has_restrictions ?? false,
        })
        localStorage.removeItem(DRAFT_STORAGE_KEY)
      }
    } catch {
      localStorage.removeItem(DRAFT_STORAGE_KEY)
    }
  }, [draftChecked, reset])

  const mutation = useMutation({
    mutationFn: participantsApi.create,
    onSuccess: () => {
      localStorage.removeItem(DRAFT_STORAGE_KEY)
      toast.success('Participante registrado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['participants'] })
      navigate('/participants')
    },
    onError: (error: unknown, data: ParticipantFormData) => {
      const detail =
        error && typeof error === 'object' && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null
      toast.error(detail || 'Erro ao registrar participante. Corrija e tente novamente.')
      try {
        localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(data))
      } catch {
        // ignore storage errors
      }
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

      <PhotoUpload setValue={setValue} />

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
          {isSubmitting ? 'Registrando...' : 'Registrar Participante'}
        </button>
      </div>
    </form>
  )
}
