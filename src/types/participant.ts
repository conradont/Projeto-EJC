export interface Participant {
  id: number
  name: string
  common_name?: string | null
  birth_date?: string | null
  instagram?: string | null
  address?: string | null
  neighborhood?: string | null
  email?: string | null
  phone?: string | null
  sacraments?: string | null
  church_movement?: string | null
  church_movement_info?: string | null
  father_name?: string | null
  father_contact?: string | null
  mother_name?: string | null
  mother_contact?: string | null
  ecc_participant?: boolean | null
  ecc_info?: string | null
  has_restrictions?: boolean | null
  restrictions_info?: string | null
  observations?: string | null
  photo_path?: string | null
}

export interface ParticipantCreate {
  name: string
  common_name?: string | null
  birth_date?: string | null
  instagram?: string | null
  address?: string | null
  neighborhood?: string | null
  email?: string | null
  phone?: string | null
  sacraments?: string | null
  church_movement?: string | null
  church_movement_info?: string | null
  father_name?: string | null
  father_contact?: string | null
  mother_name?: string | null
  mother_contact?: string | null
  ecc_participant?: boolean | null
  ecc_info?: string | null
  has_restrictions?: boolean | null
  restrictions_info?: string | null
  observations?: string | null
  photo_path?: string | null
}

export interface ParticipantUpdate extends Partial<ParticipantCreate> {}

export interface SacramentStatus {
  sacrament: 'Batismo' | 'Primeira Eucaristia' | 'Crisma'
  status: 'Concluído' | 'Não Concluído' | 'Em Processo' | 'Não Informado'
}
