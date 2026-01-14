import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-white mb-4">Bem-vindo ao Sistema EJC</h2>
        <p className="text-gray-400 text-lg">
          Sistema de gerenciamento de participantes do Encontro de Jovens com Cristo
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Link
          to="/register"
          className="bg-gray-800 p-6 rounded-xl border border-gray-700 hover:border-primary-500 transition-colors"
        >
          <h3 className="text-xl font-semibold text-white mb-2">Novo Registro</h3>
          <p className="text-gray-400">
            Cadastre um novo participante no sistema
          </p>
        </Link>

        <Link
          to="/participants"
          className="bg-gray-800 p-6 rounded-xl border border-gray-700 hover:border-primary-500 transition-colors"
        >
          <h3 className="text-xl font-semibold text-white mb-2">Participantes</h3>
          <p className="text-gray-400">
            Visualize e gerencie a lista de participantes
          </p>
        </Link>

        <Link
          to="/reports"
          className="bg-gray-800 p-6 rounded-xl border border-gray-700 hover:border-primary-500 transition-colors"
        >
          <h3 className="text-xl font-semibold text-white mb-2">Relatórios</h3>
          <p className="text-gray-400">
            Gere PDFs individuais ou completos
          </p>
        </Link>
      </div>
    </div>
  )
}
