// Your JavaScript code for handling dropdown/submenu behavior

document.addEventListener("DOMContentLoaded", function () {
    // Code to run when the DOM is ready
  
    // Example: Add your dropdown logic here
    const menuItems = document.querySelectorAll('.sidebar-menu li');
  
    menuItems.forEach(item => {
      item.addEventListener('mouseover', function () {
        const submenu = item.querySelector('.submenu');
        if (submenu) {
          submenu.style.display = 'block';
        }
      });
  
      item.addEventListener('mouseout', function () {
        const submenu = item.querySelector('.submenu');
        if (submenu) {
          submenu.style.display = 'none';
        }
      });
    });
  });
  