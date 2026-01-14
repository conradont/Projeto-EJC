import { forwardRef, InputHTMLAttributes, useEffect, useState, useCallback } from 'react'
import { FieldError, UseFormRegisterReturn, Control, useWatch } from 'react-hook-form'
import { maskDate, maskPhone, formatDateToBrazilian } from '@/lib/masks'
import { ParticipantFormData } from '@/schemas/participant'

interface MaskedInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'onBlur'> {
  label: string
  error?: FieldError
  mask: 'date' | 'phone' | 'email'
  register: UseFormRegisterReturn
  control?: Control<ParticipantFormData>
}

const MaskedInput = forwardRef<HTMLInputElement, MaskedInputProps>(
  ({ label, error, mask, register, control, ...props }, ref) => {
    const [displayValue, setDisplayValue] = useState<string>('')
    const fieldName = register.name as keyof ParticipantFormData
    const formValue = control ? useWatch({ control, name: fieldName }) : undefined

    // Função para atualizar o display value baseado no valor fornecido
    const updateDisplayFromValue = useCallback((value: string | null | undefined) => {
      if (!value || value === '') {
        setDisplayValue('')
        return
      }
      
      const valueStr = String(value)
      
      if (mask === 'date') {
        // Se vier do backend no formato ISO (YYYY-MM-DD), converte para brasileiro
        if (/^\d{4}-\d{2}-\d{2}$/.test(valueStr)) {
          setDisplayValue(formatDateToBrazilian(valueStr))
        } else {
          setDisplayValue(maskDate(valueStr))
        }
      } else if (mask === 'phone') {
        setDisplayValue(maskPhone(valueStr))
      } else {
        // Email - apenas exibe o valor sem máscara
        setDisplayValue(valueStr)
      }
    }, [mask])

    // Sincroniza com o valor do formulário quando ele muda (ex: reset)
    useEffect(() => {
      // Se temos control, usa o valor do watch para sincronizar
      if (control) {
        updateDisplayFromValue(formValue)
      } else {
        // Se não temos control, verifica o valor do input após montar
        const timer = setTimeout(() => {
          const inputElement = register.ref.current
          if (inputElement?.value) {
            updateDisplayFromValue(inputElement.value)
          }
        }, 0)
        return () => clearTimeout(timer)
      }
    }, [formValue, mask, control, updateDisplayFromValue])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = e.target.value
      let maskedValue = ''

      if (mask === 'date') {
        maskedValue = maskDate(inputValue)
      } else if (mask === 'phone') {
        maskedValue = maskPhone(inputValue)
      } else {
        // Email não tem máscara visual, apenas validação
        maskedValue = inputValue
      }

      setDisplayValue(maskedValue)

      // Atualiza o valor no formulário através do register
      const syntheticEvent = {
        ...e,
        target: {
          ...e.target,
          value: maskedValue,
        },
      }

      register.onChange(syntheticEvent)
    }

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      register.onBlur(e)
    }

    return (
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          {label}
        </label>
        <input
          {...props}
          {...register}
          ref={(e) => {
            register.ref(e)
            if (typeof ref === 'function') {
              ref(e)
            } else if (ref) {
              ref.current = e
            }
          }}
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`w-full px-4 py-2 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
            error ? 'border-red-500' : 'border-gray-600'
          }`}
        />
        {error && (
          <p className="mt-1 text-sm text-red-400">{error.message}</p>
        )}
      </div>
    )
  }
)

MaskedInput.displayName = 'MaskedInput'

export default MaskedInput
