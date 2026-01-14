import { forwardRef, TextareaHTMLAttributes } from 'react'
import { FieldError } from 'react-hook-form'

interface TextAreaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string
  error?: FieldError
}

const TextAreaField = forwardRef<HTMLTextAreaElement, TextAreaFieldProps>(
  ({ label, error, ...props }, ref) => {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          {label}
        </label>
        <textarea
          ref={ref}
          {...props}
          rows={4}
          className={`w-full px-4 py-2 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-y ${
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

TextAreaField.displayName = 'TextAreaField'

export default TextAreaField
