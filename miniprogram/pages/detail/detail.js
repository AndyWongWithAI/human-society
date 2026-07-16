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

function getNodeMap() {
  const map = {}
  app.globalData.nodes.forEach(n => map[n.id] = n)
  return map
}
function getUpstream(id) {
  return app.globalData.edges.filter(e => e.source === id)
    .map(e => ({ id: e.target, relation: e.relation_label || e.relation }))
}
function getDownstream(id) {
  return app.globalData.edges.filter(e => e.target === id)
    .map(e => ({ id: e.source, relation: e.relation_label || e.relation }))
}
function getArticles(id) {
  const api = require('../../utils/api')
  return api.getArticles(id)
}

Page({
  data: {
    node: null,
    upstream: [],
    downstream: [],
    articles: [],
    stmtExpanded: false,
    loading: true
  },

  _pollTimer: null,

  onLoad(options) {
    if (app.globalData.loaded) {
      this.loadNode(options.id)
    } else if (app.globalData.loadError) {
      this.setData({ loading: false })
    } else {
      this._pollTimer = setInterval(() => {
        if (app.globalData.loaded) {
          clearInterval(this._pollTimer)
          this.loadNode(options.id)
        } else if (app.globalData.loadError) {
          clearInterval(this._pollTimer)
          this.setData({ loading: false })
        }
      }, 300)
    }
  },

  onUnload() {
    if (this._pollTimer) clearInterval(this._pollTimer)
  },

  loadNode(id) {
    const nodeMap = getNodeMap()
    const n = nodeMap[id]
    if (!n) {
      wx.showToast({ title: '未找到: ' + id, icon: 'none' })
      this.setData({ loading: false })
      return
    }

    const upstream = getUpstream(id).map(e => this._formatDep(e, 'up', nodeMap))
    const downstream = getDownstream(id).map(e => this._formatDep(e, 'down', nodeMap))
    const articles = getArticles(id)

    const created = n.created || ''
    const revised = n.revised || ''
    let dateInfo = ''
    if (created) {
      dateInfo = '创建于 ' + created
      if (revised && revised !== created) dateInfo += ' · 修订于 ' + revised
    }

    const STATUS_LABELS = {
      verified: '已验证', 'verified*': '已验证*', weakly_verified: '弱验证',
      candidate: '候选', rejected: '已驳回'
    }

    this.setData({
      loading: false,
      node: {
        id: n.id,
        term: n.term,
        term_zh: n.term_zh,
        type: n.type,
        layer: n.layer,
        status: n.status,
        statement: n.statement || '',
        dotColor: TYPE_COLORS[n.type] || '#999',
        typeLabel: TYPE_LABELS[n.type] || n.type,
        layerLabel: app.globalData.layerLabels[n.layer] || n.layer,
        statusLabel: STATUS_LABELS[n.status] || '',
        summary: n['人话摘要'] || '',
        dateInfo
      },
      upstream,
      downstream,
      articles,
      stmtExpanded: false
    })
  },

  _formatDep(e, dir, nodeMap) {
    const refId = dir === 'up' ? e.id : e.id
    const n = nodeMap[refId]
    if (!n) return {
      id: refId, _unique: refId,
      term_zh: '?', dotColor: '#999', typeLabel: '', relation: e.relation
    }
    return {
      id: n.id,
      _unique: n.id + '_' + dir,
      term_zh: n.term_zh || n.term,
      term: n.term,
      dotColor: TYPE_COLORS[n.type] || '#999',
      typeLabel: TYPE_LABELS[n.type] || n.type,
      relation: e.relation,
      excerpt: (n['人话摘要'] || '').slice(0, 50)
    }
  },

  toggleStmt() {
    this.setData({ stmtExpanded: !this.data.stmtExpanded })
  },

  goNode(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    wx.redirectTo({ url: `/pages/detail/detail?id=${id}` })
  }
})
