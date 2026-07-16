#!/usr/bin/env node
/**
 * 小程序静态验证 — 无需微信开发者工具
 * 检查 app.json 合法性、页面文件完整性、常见 WXML 错误
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
let errors = 0
let warnings = 0

function err(msg) { console.error('❌ ' + msg); errors++ }
function warn(msg) { console.warn('⚠️  ' + msg); warnings++ }
function ok(msg) { console.log('✅ ' + msg) }

// 1. app.json
ok('=== app.json ===')
const appJsonPath = path.join(ROOT, 'app.json')
let appJson
try {
  appJson = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'))
} catch (e) {
  err('app.json 解析失败: ' + e.message)
  process.exit(1)
}

// Check required fields
if (!appJson.pages || !Array.isArray(appJson.pages)) {
  err('app.json 必须包含 pages 数组')
} else {
  ok(`pages: ${appJson.pages.length} 个页面`)
}

// Check tabBar if present
if (appJson.tabBar) {
  const list = appJson.tabBar.list || []
  if (list.length < 2) {
    err(`tabBar.list 至少需要 2 项，当前 ${list.length} 项`)
  } else {
    ok(`tabBar: ${list.length} 个 tab`)
  }
} else {
  ok('无 tabBar（合法）')
}

// 2. Check all page paths exist
ok('=== 页面文件 ===')
const pages = appJson.pages || []
const wxmlIssues = []

pages.forEach(pagePath => {
  const base = path.join(ROOT, pagePath)
  const checks = ['.wxml', '.js', '.wxss', '.json']
  let missing = []
  checks.forEach(ext => {
    const full = base + ext
    if (!fs.existsSync(full)) {
      missing.push(ext)
    }
  })

  if (missing.length > 0) {
    // .json is optional
    const req = missing.filter(e => e !== '.json')
    if (req.length > 0) {
      err(`页面 ${pagePath} 缺少: ${req.join(', ')}`)
    } else {
      warn(`页面 ${pagePath} 缺少 .json（可选）`)
    }
  } else {
    ok(`${pagePath}/`)
  }

  // Check WXML for common issues
  const wxmlPath = base + '.wxml'
  if (fs.existsSync(wxmlPath)) {
    const wxml = fs.readFileSync(wxmlPath, 'utf8')

    // Check wx:for without wx:key
    const forMatches = wxml.match(/wx:for/g)
    const keyMatches = wxml.match(/wx:key/g)
    if (forMatches) {
      const forCount = forMatches.length
      const keyCount = keyMatches ? keyMatches.length : 0
      if (forCount !== keyCount) {
        warn(`${pagePath}.wxml: wx:for 出现 ${forCount} 次，wx:key 出现 ${keyCount} 次（应一一对应）`)
      }
    }

    // Check unmatched tags
    const openView = (wxml.match(/<view/g) || []).length
    const closeView = (wxml.match(/<\/view>/g) || []).length
    if (openView !== closeView) {
      err(`${pagePath}.wxml: <view> 标签不配对 (开 ${openView}, 闭 ${closeView})`)
    }
    const openBlock = (wxml.match(/<block/g) || []).length
    const closeBlock = (wxml.match(/<\/block>/g) || []).length
    if (openBlock !== closeBlock) {
      err(`${pagePath}.wxml: <block> 标签不配对 (开 ${openBlock}, 闭 ${closeBlock})`)
    }
    const openScroll = (wxml.match(/<scroll-view/g) || []).length
    const closeScroll = (wxml.match(/<\/scroll-view>/g) || []).length
    if (openScroll !== closeScroll) {
      err(`${pagePath}.wxml: <scroll-view> 标签不配对 (开 ${openScroll}, 闭 ${closeScroll})`)
    }

    // Check wx:key values match data fields
    const keyPattern = /wx:key="([^"]+)"/g
    let km
    while ((km = keyPattern.exec(wxml)) !== null) {
      const key = km[1]
      if (key === 'unique' || key === 'id') {
        warn(`${pagePath}.wxml: wx:key="${key}" 可能无效，建议用 "_unique"`)
      }
    }
  }
})

// 3. Check utils
ok('=== 工具模块 ===')
const utilsPath = path.join(ROOT, 'utils', 'api.js')
if (fs.existsSync(utilsPath)) {
  ok('utils/api.js')
} else {
  err('utils/api.js 缺失')
}

// 4. Check app.js
ok('=== 入口文件 ===')
const appJs = path.join(ROOT, 'app.js')
if (fs.existsSync(appJs)) {
  ok('app.js')
  const content = fs.readFileSync(appJs, 'utf8')
  if (!content.includes('App(')) err('app.js 缺少 App() 调用')
} else {
  err('app.js 缺失')
}

// Summary
console.log(`\n=== 结果: ${errors} 个错误, ${warnings} 个警告 ===`)
process.exit(errors > 0 ? 1 : 0)
