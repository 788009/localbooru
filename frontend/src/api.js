import axios from 'axios'

const host = __API_HOST__ || window.location.hostname
const port = __API_PORT__ || 8000
const serverOrigin = `http://${host}:${port}`

const api = axios.create({
  baseURL: `${serverOrigin}/api`
})

export default {
  getConfig() {
    return api.get('/config').then(res => res.data)
  },
  autocomplete(query) {
    return api.get('/search/autocomplete', { params: { q: query } }).then(res => res.data)
  },
  search(data) {
    return api.post('/search', data).then(res => res.data)
  },
  getImageDetail(id) {
    return api.get(`/images/${id}/detail`).then(res => res.data)
  },
  getImageUrl(id) {
    return `${serverOrigin}/api/images/${id}/file`
  }
}
