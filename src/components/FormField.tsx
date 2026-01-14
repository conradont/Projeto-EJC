import { forwardRef, InputHTMLAttributes } from 'react'
import { FieldError } from 'react-hook-form'

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: FieldError
}

const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, ...props }, ref) => {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          {label}
        </label>
        <input
          ref={ref}
          {...props}
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

FormField.displayName = 'FormField'

export default FormField
