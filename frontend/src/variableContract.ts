export type ConfirmedVariableType = 'numeric' | 'binary' | 'categorical' | 'date/time' | 'identifier' | 'text'

export type VariableContract = {
  file: string
  sheet: string
  name: string
  confirmed_type: ConfirmedVariableType
  coding: Record<string, string | number>
  analysis_role?: 'auto' | 'outcome' | 'exposure' | 'covariate' | 'identifier' | 'exclude'
}

const KEY = 'medicalAnalytics.variableContract'

export function saveVariableContract(contract: VariableContract[]) {
  if (typeof window === 'undefined') return
  sessionStorage.setItem(KEY, JSON.stringify(contract))
  sessionStorage.setItem('variableReviewComplete', 'true')
  sessionStorage.setItem('variableContractReady', 'true')
}

export function loadVariableContract(): VariableContract[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = sessionStorage.getItem(KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function clearVariableContract() {
  if (typeof window === 'undefined') return
  sessionStorage.removeItem(KEY)
  sessionStorage.removeItem('variableReviewComplete')
  sessionStorage.removeItem('variableContractReady')
}

export function isVariableContractReady() {
  if (typeof window === 'undefined') return false
  return sessionStorage.getItem('variableContractReady') === 'true' && loadVariableContract().length > 0
}

export function variablesByType(contract: VariableContract[], type: ConfirmedVariableType) {
  return contract.filter(v => v.confirmed_type === type)
}

export function variableNames(contract: VariableContract[], type?: ConfirmedVariableType) {
  return (type ? variablesByType(contract, type) : contract).map(v => v.name)
}
