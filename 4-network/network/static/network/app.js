document.addEventListener('DOMContentLoaded', function() {






    document.querySelector('#posts').addEventListener('click', (e) => {
        
        if (e.target.className == 'btn btn-sm btn-outline-primary edit') {
            
            let post = e.target.parentNode;
            let content = post.querySelector('.text').innerHTML;

            let input = document.createElement('textarea');
            input.className = 'newtext form-control';
            input.maxLength = "1000";
            input.innerHTML = content;

            let button = document.createElement('button');
            button.className = "btn btn-sm btn-outline-primary save";
            button.innerHTML = "Save";
            
            post.querySelector('.text').style.display = 'none';
            post.querySelector('.edit').style.display = 'none';
            post.appendChild(input);
            post.appendChild(button);
        }

        else if (e.target.className == 'btn btn-sm btn-outline-primary save') {
            
            let post = e.target.parentNode;
            let newtext = post.querySelector('.newtext').value;
            
            fetch(`/edit/${post.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    text: newtext
                })
            })

            .then(result => {
                if (result.status != 204) {
                    alert(`You can't do that`)
                }
                else {
                    
                    post.removeChild(post.querySelector('.newtext'));
                    post.removeChild(post.querySelector('.save'));
                    post.querySelector('.text').style.display = 'block';
                    post.querySelector('.text').innerHTML = newtext;
                    post.querySelector('.edit').style.display = 'block';
                }
            })
        }

        else if (e.target.className == 'far fa-heart') {

            let post = e.target.parentNode;

            fetch(`/like/${post.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    like: true
                })
            })
            .then(result => {
                if (result.status == 204) {
                    e.target.style.display = 'none';
                    post.querySelector('.fas').style.display = 'block';
                    let likes = parseInt(post.querySelector('.likes').innerHTML);
                    post.querySelector('.likes').innerHTML = likes + 1;
                }
            })
        }

        else if (e.target.className == 'fas fa-heart') {

            let post = e.target.parentNode;

            fetch(`/like/${post.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    like: false
                })
            })
            .then((result) => {
                if (result.status == 204) {

                    e.target.style.display = 'none';
                    post.querySelector('.far').style.display = 'block';
                    let likes = parseInt(post.querySelector('.likes').innerHTML);
                    post.querySelector('.likes').innerHTML = likes - 1;
                }
            })

        }

    })



})