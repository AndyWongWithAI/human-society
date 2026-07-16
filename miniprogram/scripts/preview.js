#!/usr/bin/env node
/**
 * 生成小程序预览二维码 — 无需开发者工具
 * 先跑 validate.js，通过后再跑本脚本
 */
const ci = require('miniprogram-ci')
const path = require('path')
const fs = require('fs')

const ROOT = path.resolve(__dirname, '..')
const QR_PATH = path.join(ROOT, 'preview-qrcode.png')

async function main() {
  // 先验证
  console.log('🔍 静态验证…')
  try {
    require('child_process').execSync(`node "${path.join(__dirname, 'validate.js')}"`, {
      cwd: ROOT, stdio: 'inherit'
    })
  } catch (e) {
    console.error('验证未通过，终止预览')
    process.exit(1)
  }

  const project = new ci.Project({
    appid: 'wx167514146b03982c',
    type: 'miniProgram',
    projectPath: ROOT,
    privateKeyPath: path.join(ROOT, 'private.key'),
    ignores: ['node_modules/**/*', 'scripts/**/*', 'private.key', 'package*.json']
  })

  console.log('📤 生成预览…')
  try {
    const previewResult = await ci.preview({
      project,
      desc: '自动预览',
      setting: {
        es6: true,
        minify: true,
        urlCheck: true
      },
      qrcodeFormat: 'image',
      qrcodeOutputDest: QR_PATH,
      onProgressUpdate: (info) => {
        if (info && info.status) console.log('  ' + info.status)
      }
    })
    console.log('✅ 预览二维码已生成: ' + QR_PATH)
    console.log('用微信扫码即可预览')
  } catch (e) {
    if (e.message && e.message.includes('ip')) {
      console.error('❌ IP 白名单未通过')
      console.error('请在微信后台 → 开发 → 开发设置 → IP 白名单中添加本机 IP')
    } else {
      console.error('❌ 预览失败: ' + (e.message || e))
    }
    process.exit(1)
  }
}

main()
