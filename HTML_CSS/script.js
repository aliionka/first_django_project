document.addEventListener('DOMContentLoaded', function(){
    var container = document.querySelector('.modal');
    var popupButtons = document.querySelectorAll('.light-button');
    var closeBtn = document.querySelector('.close');


    for (let i = 0; i < popupButtons.length; i++) {
        popupButtons[i].addEventListener('click', function(){
            container.style.display = 'flex';
    });
}


container.addEventListener('click', function(event){
    if(event.target == container) {
        container.style.display = 'none';
        }
    });
});


if (closeBtn) {
        closeBtn.addEventListener('click', function(){
            container.style.display = 'none';
        });
    }
