/**
 * Utilitários para aplicar e remover máscaras de campos de formulário
 */

/**
 * Aplica máscara de data no formato DD/MM/AAAA
 */
export function maskDate(value: string): string {
  // Remove tudo que não é número
  const numbers = value.replace(/\D/g, '')
  
  // Limita a 8 dígitos
  const limited = numbers.slice(0, 8)
  
  // Aplica a máscara DD/MM/AAAA
  if (limited.length <= 2) {
    return limited
  } else if (limited.length <= 4) {
    return `${limited.slice(0, 2)}/${limited.slice(2)}`
  } else {
    return `${limited.slice(0, 2)}/${limited.slice(2, 4)}/${limited.slice(4)}`
  }
}

/**
 * Remove máscara de data e retorna no formato YYYY-MM-DD (ISO)
 */
export function unmaskDate(value: string): string | null {
  if (!value) return null
  
  // Remove tudo que não é número
  const numbers = value.replace(/\D/g, '')
  
  // Se não tiver 8 dígitos, retorna null
  if (numbers.length !== 8) return null
  
  const day = numbers.slice(0, 2)
  const month = numbers.slice(2, 4)
  const year = numbers.slice(4, 8)
  
  // Valida se a data é válida
  const dayNum = parseInt(day, 10)
  const monthNum = parseInt(month, 10)
  const yearNum = parseInt(year, 10)
  
  if (dayNum < 1 || dayNum > 31) return null
  if (monthNum < 1 || monthNum > 12) return null
  if (yearNum < 1900 || yearNum > 2100) return null
  
  // Retorna no formato ISO YYYY-MM-DD
  return `${year}-${month}-${day}`
}

/**
 * Converte data ISO (YYYY-MM-DD) para formato brasileiro (DD/MM/AAAA)
 */
export function formatDateToBrazilian(isoDate: string | null | undefined): string {
  if (!isoDate) return ''
  
  const [year, month, day] = isoDate.split('-')
  if (!year || !month || !day) return ''
  
  return `${day}/${month}/${year}`
}

/**
 * Aplica máscara de telefone no formato (00) 00000-0000
 */
export function maskPhone(value: string): string {
  // Remove tudo que não é número
  const numbers = value.replace(/\D/g, '')
  
  // Limita a 11 dígitos
  const limited = numbers.slice(0, 11)
  
  // Aplica a máscara conforme o tamanho
  if (limited.length <= 2) {
    return limited.length > 0 ? `(${limited}` : ''
  } else if (limited.length <= 7) {
    return `(${limited.slice(0, 2)}) ${limited.slice(2)}`
  } else if (limited.length <= 10) {
    return `(${limited.slice(0, 2)}) ${limited.slice(2, 6)}-${limited.slice(6)}`
  } else {
    return `(${limited.slice(0, 2)}) ${limited.slice(2, 7)}-${limited.slice(7)}`
  }
}

/**
 * Remove máscara de telefone
 */
export function unmaskPhone(value: string): string {
  return value.replace(/\D/g, '')
}

/**
 * Valida formato de email e aplica normalização básica
 */
export function normalizeEmail(value: string): string {
  if (!value) return ''
  
  // Remove espaços em branco
  const trimmed = value.trim().toLowerCase()
  
  return trimmed
}

/**
 * Valida se o email tem formato válido
 */
export function isValidEmail(email: string): boolean {
  if (!email) return true // Email é opcional
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}
