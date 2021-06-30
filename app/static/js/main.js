//Sign Up form validator
const signupForm =document.querySelector('form')

signupForm.addEventListener('submit',(e)=>{
    e.preventDefault()
    const username =signupForm['username'].value
    const email = signupForm['email'].value
    const password = signupForm['password'].value
    const confirmPassword = signupForm['confirm-password'].value

    if(username===''){
        failureError('username','Username cannot be empty')
    }
    else{
        success('username')
    }

    if(email===''){
        failureError('email','Email cannot be empty')
    }
    else if(!isEmailValid(email)){
        failureError('email','Enter a valid email')
    }
    else{
        success('email')
    }

    if(password===''){
        failureError('password','Password cannot be empty')
    }
    else{
        success('password')
    }

    if(confirmPassword===''){
        failureError('confirm-password','Confirm Password cannot be empty')
    }

    else if(password !== confirmPassword){
        failureError('confirm-password','Passwords do not match')
    }
    else{
        success('confirm-password')
    }

})
function failureError(input,message){
        const formInput =signupForm[input].parentNode
        formInput.classList.add('error')

        const span=formInput.querySelector('span')
        span.innerText=message
        span.style.opacity='1'
}
function success(input){
        const formInput =signupForm[input].parentNode
        formInput.classList.remove('error')
        const span=formInput.querySelector('span')
        span.style.opacity='0'
}

// email regex function
function isEmailValid(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}
