// login form validator
const loginForm = document.querySelector('form')

loginForm.addEventListener('submit',(e)=>{
    e.preventDefault()
    const loginUsername=loginForm['username'].value
    const loginPassword= loginForm['password'].value

    if(loginUsername===''){
        failureError('username','Username cannot be empty')
    }
    else{
        success('username')
    }

    if(loginPassword===''){
        failureError('password','Password cannot be empty')
    }
    else{
        success('password')
        loginForm.submit()
    }

})
function failureError(input,message){
        const formInput =loginForm[input].parentNode
        formInput.classList.add('error')

        const span=formInput.querySelector('span')
        span.innerText=message
        span.style.opacity='1'
}
function success(input){
        const formInput =loginForm[input].parentNode
        formInput.classList.remove('error')
        const span=formInput.querySelector('span')
        span.style.opacity='0'
}
