// forgot password form validator
const forgotForm = document.querySelector('form')

forgotForm.addEventListener('submit',(e)=>{
    e.preventDefault()
    const email=forgotForm['email'].value

    if(email===''){
        failureError('email','Email cannot be empty')
    }
    else if(!isEmailValid(email)){
        failureError('email','Enter a valid email')
    }
    else{
        success('email')

        forgotForm.submit()
    }

})
function failureError(input,message){
        const formInput =forgotForm[input].parentNode
        formInput.classList.add('error')

        const span=formInput.querySelector('span')
        span.innerText=message
        span.style.opacity='1'
}
function success(input){
        const formInput =forgotForm[input].parentNode
        formInput.classList.remove('error')
        const span=formInput.querySelector('span')
        span.style.opacity='0'
}

// email regex function
function isEmailValid(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}