import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const client = axios.create({ baseURL: BASE })

client.interceptors.request.use(config => {
    const token = localStorage.getItem('jwt')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

export default client