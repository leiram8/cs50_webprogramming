document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

  // By default, load the inbox
  load_mailbox('inbox');


  const content = document.querySelector('#compose-body');
  const subject = document.querySelector('#compose-subject');
  const recipients = document.querySelector('#compose-recipients');

  // Send email and load mailbox on submit
  document.querySelector('form').onsubmit = () => {
    
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: recipients.value,
        subject: subject.value,
        body: content.value
      })
    })
    .then(response => response.json())
    .then(result => {
      console.log(result);
      load_mailbox('sent');
    })
    return false;
  }

  // Show email when its clicked
  document.addEventListener('click', event => {
    const email = event.target
    if (email.className === 'mail') {
      fetch(`/emails/${email.id}`)
      .then(response => response.json())
      .then(email => {
        show_mail(email);
      })
    }
  })


  // Unarchive an email
  unarchive = document.querySelector('#unarchive');
  unarchive.addEventListener('click', () => {
    id = localStorage.getItem('id');
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: false
      })
    })
    .then(() => {
      load_mailbox('inbox');
    });
  });
  
  // Archive an email
  archive = document.querySelector('#archive');
  archive.addEventListener('click', () => {
    id = localStorage.getItem('id');
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: true
      })
    })
    .then(() => {
      load_mailbox('inbox');
    });
  });

  // Reply email
  document.querySelector('#reply-mail').addEventListener('click', () => {
    id = localStorage.getItem('id');
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {

      // Pre-fill the composition form
      const replysender = email.sender;
      let title = email.subject;
      if (title.slice(0, 4) != 'Re: ') {
        title = 'Re: ' + title;
      }
      const data = `On ${email.timestamp} ${replysender} wrote: 
`;
      const body = data + email.body;
      compose_email(replysender, title, body);
    });
  });

  
});

function compose_email(recipients='', subject='', body='') {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#mail-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = recipients;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = body;
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  localStorage.setItem('mailbox', mailbox);
  
  // Render each mail
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(add_mail);
  }); 
}

function add_mail(data) {
  const mail = document.createElement('div');
  mail.className = 'mail';
  mail.id = data.id;
  mail.innerHTML = `<span class='sender'>${data.sender}</span><span class='subject'>${data.subject}</span><span class='date'>${data.timestamp}</span>`;
  
  // mark mail as read
  if (data.read) {
    mail.style.backgroundColor = 'lightgray';
  }

  document.querySelector('#emails-view').append(mail);
}

function show_mail(data) {

  // show mail, hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'block';

  // display email
  document.querySelector('#from-mail').innerHTML = data.sender;
  document.querySelector('#to-mail').innerHTML = data.recipients;
  document.querySelector('#subject-mail').innerHTML = data.subject;
  document.querySelector('#body-mail').innerHTML = data.body;
  document.querySelector('#timestamp-mail').innerHTML = data.timestamp;

  // hide buttons
  document.querySelector('#unarchive').style.display = 'none';
  document.querySelector('#archive').style.display = 'none';

  // show archive button
  if (localStorage.getItem('mailbox') === 'inbox') {
    document.querySelector('#archive').style.display = 'block';
  }

  // show unarchive button
  else if (localStorage.getItem('mailbox') === 'archive') {
    document.querySelector('#unarchive').style.display = 'block';
  }
  
  // save mail id
  localStorage.setItem('id', data.id);

  // mark as read
  fetch(`/emails/${data.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  });

}