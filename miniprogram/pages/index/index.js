const api = require('../../utils/api')
const app = getApp()

const TYPE_COLORS = {
  physical_constraint: '#5B8FF9', concept: '#5AD8A6',
  definitional_axiom: '#F6BD16', theorem: '#9270CA',
  bridging_proposition: '#5D9CEC', deduction: '#F08080',
  composite_deduction: '#E8684A'
}
const TYPE_LABELS = {
  physical_constraint: '物理约束', concept: '概念',
  definitional_axiom: '公理', theorem: '定理',
  bridging_proposition: '桥接命题', deduction: '推论',
  composite_deduction: '复合推论'
}
const STATUS_LABELS = {
  verified: '已验证', 'verified*': '已验证*', weakly_verified: '弱验证',
  candidate: '候选', rejected: '已驳回'
}

Page({
  data: {
    layers: [],
    activeLayer: 'L0',
    query: '',
    filtered: [],
    activeId: '',
    meta: null
  },

  onLoad() {
    this.setData({
      layers: app.globalData.layerOrder.map(key => ({ key, label: app.globalData.layerLabels[key] || key, count: 0 }))
    })
    if (app.globalData.loaded) {
      this.prepareData()
    }
  },

  onDataReady() {
    this.prepareData()
  },

  onShow() {
    if (app.globalData.loaded) {
      this.prepareData()
    }
  },

  prepareData() {
    const nodes = app.globalData.nodes
    // Count by layer
    const counts = {}
    nodes.forEach(n => counts[n.layer] = (counts[n.layer] || 0) + 1)
    const layers = app.globalData.layerOrder.map(key => ({
      key, label: app.globalData.layerLabels[key] || key,
      count: counts[key] || 0
    }))
    this.setData({ layers, meta: api.getData() ? api.getData().meta : null })
    this.filterNodes()
  },

  switchLayer(e) {
    const layer = e.currentTarget.dataset.layer
    this.setData({ activeLayer: layer, activeId: '', query: '' })
    this.filterNodes(layer)
  },

  onSearch(e) {
    const query = e.detail.value
    this.setData({ query })
    this.filterNodes(this.data.activeLayer, query)
  },

  clearSearch() {
    this.setData({ query: '' })
    this.filterNodes(this.data.activeLayer, '')
  },

  filterNodes(layer, query) {
    layer = layer || this.data.activeLayer
    query = (query !== undefined ? query : this.data.query).toLowerCase()
    const nodes = app.globalData.nodes

    let filtered = nodes.filter(n => {
      if (query) {
        return n.id.toLowerCase().includes(query) ||
          (n.term || '').toLowerCase().includes(query) ||
          (n.term_zh || '').toLowerCase().includes(query) ||
          (n['人话摘要'] || '').toLowerCase().includes(query)
      }
      return n.layer === layer
    })

    // Sort: newest first
    filtered.sort((a, b) => {
      const da = a.created || '0000'
      const db = b.created || '0000'
      if (da !== db) return db.localeCompare(da)
      return (a.id || '').localeCompare(b.id || '')
    })

    // Read tracking
    let readIds = new Set()
    try {
      readIds = new Set(wx.getStorageSync('hs-read-ids') || [])
    } catch (e) { }

    const now = Date.now()
    // If searching, group by layer
    if (query) {
      const byLayer = {}
      filtered.forEach(n => {
        if (!byLayer[n.layer]) byLayer[n.layer] = []
        byLayer[n.layer].push(n)
      })
      const result = []
      let uid = 0
      app.globalData.layerOrder.forEach(l => {
        if (byLayer[l] && byLayer[l].length > 0) {
          result.push({ _header: true, _unique: 'h_' + (uid++), _label: app.globalData.layerLabels[l] + ' (' + byLayer[l].length + ')' })
          byLayer[l].forEach(n => result.push(this._formatNode(n, readIds, now, uid++)))
        }
      })
      this.setData({ filtered: result })
    } else {
      this.setData({ filtered: filtered.map((n, i) => this._formatNode(n, readIds, now, i)) })
    }
  },

  _formatNode(n, readIds, now, uid) {
    const created = n.created || ''
    const isNew = created && !readIds.has(n.id) && ((now - new Date(created).getTime()) / 86400000 < 14)
    const d = created ? new Date(created) : null
    const dateDisplay = d ? `${d.getMonth() + 1}/${d.getDate()}` : ''
    return {
      ...n,
      _unique: n.id + '_' + (uid !== undefined ? uid : 0),
      dotColor: TYPE_COLORS[n.type] || '#999',
      typeLabel: TYPE_LABELS[n.type] || n.type,
      statusLabel: STATUS_LABELS[n.status] || '',
      statusClass: 'badge-' + (n.status === 'verified' || n.status === 'verified*' ? 'verified' : (n.status || 'candidate')),
      dateDisplay,
      isNew,
      excerpt: (n['人话摘要'] || '').slice(0, 60)
    }
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    this.setData({ activeId: id })

    // Mark as read
    try {
      let ids = wx.getStorageSync('hs-read-ids') || []
      if (ids.indexOf(id) === -1) {
        ids.push(id)
        wx.setStorageSync('hs-read-ids', ids)
        this.filterNodes() // re-render to remove NEW badge
      }
    } catch (e) { }

    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  }
})
