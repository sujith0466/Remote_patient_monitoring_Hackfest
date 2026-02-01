const ROLE_KEY = "carewatch_role"

export function setRole(role){
  localStorage.setItem(ROLE_KEY, role)
}

export function getRole(){
  return localStorage.getItem(ROLE_KEY)
}

export function clearRole(){
  localStorage.removeItem(ROLE_KEY)
}
