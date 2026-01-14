import { z } from 'zod'
import {
  maskDate,
  unmaskDate,
  formatDateToBrazilian,
  maskPhone,
  unmaskPhone,
  normalizeEmail,
  isValidEmail,
} from '@/lib/masks'

const phoneRegex = /^[0-9]{10,11}$/ // Apenas números após remover máscara
const instagramRegex = /^@?[a-zA-Z0-9._]+$/

export const participantSchema = z.object({
  name: z.string().min(1, 'Nome completo é obrigatório').max(200),
  common_name: z.string().max(200).optional().nullable(),
  birth_date: z
    .string()
    .transform((val) => {
      // Se vier no formato brasileiro DD/MM/AAAA, converte para ISO
      if (!val) return null
      const unmasked = unmaskDate(val)
      return unmasked || val // Se não conseguir converter, retorna o valor original
    })
    .refine((val) => !val || /^\d{4}-\d{2}-\d{2}$/.test(val), {
      message: 'Data inválida. Use o formato DD/MM/AAAA',
    })
    .optional()
    .nullable(),
  instagram: z
    .string()
    .max(100)
    .refine((val) => !val || instagramRegex.test(val), {
      message: 'Instagram inválido',
    })
    .optional()
    .nullable(),
  address: z.string().max(500).optional().nullable(),
  neighborhood: z.string().max(200).optional().nullable(),
  email: z
    .string()
    .transform((val) => normalizeEmail(val || ''))
    .refine((val) => !val || isValidEmail(val), {
      message: 'Email inválido',
    })
    .optional()
    .nullable()
    .or(z.literal('')),
  phone: z
    .string()
    .transform((val) => {
      if (!val) return null
      const unmasked = unmaskPhone(val)
      return unmasked.length >= 10 ? unmasked : null
    })
    .refine((val) => !val || phoneRegex.test(val), {
      message: 'Telefone inválido. Digite pelo menos 10 dígitos',
    })
    .optional()
    .nullable(),
  sacraments: z.string().optional().nullable(),
  church_movement: z.string().max(200).optional().nullable(),
  church_movement_info: z.string().max(500).optional().nullable(),
  father_name: z.string().max(200).optional().nullable(),
  father_contact: z
    .string()
    .transform((val) => {
      if (!val) return null
      const unmasked = unmaskPhone(val)
      return unmasked.length >= 10 ? unmasked : null
    })
    .refine((val) => !val || phoneRegex.test(val), {
      message: 'Contato do pai inválido. Digite pelo menos 10 dígitos',
    })
    .optional()
    .nullable(),
  mother_name: z.string().max(200).optional().nullable(),
  mother_contact: z
    .string()
    .transform((val) => {
      if (!val) return null
      const unmasked = unmaskPhone(val)
      return unmasked.length >= 10 ? unmasked : null
    })
    .refine((val) => !val || phoneRegex.test(val), {
      message: 'Contato da mãe inválido. Digite pelo menos 10 dígitos',
    })
    .optional()
    .nullable(),
  ecc_participant: z.boolean().optional().nullable(),
  ecc_info: z.string().max(500).optional().nullable(),
  has_restrictions: z.boolean().optional().nullable(),
  restrictions_info: z.string().max(500).optional().nullable(),
  observations: z.string().optional().nullable(),
  photo_path: z.string().optional().nullable(),
})

export type ParticipantFormData = z.infer<typeof participantSchema>
