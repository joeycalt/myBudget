// $(".navbar-burger").click(function () {
//     // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
//     $(".navbar-burger").toggleClass("is-active");
//     $(".navbar-menu").toggleClass("is-active");
//   });

  $(".counter").each(function () {
    let $this = $(this),
      countTo = $this.attr("data-countto");
    countDuration = parseInt($this.attr("data-duration"));
    $({ counter: $(this).text()}).animate(
      {
        counter: countTo
      },
      {
        duration: countDuration,
        fpsInterval: '1000',
        step: function () {
          $this.text(Math.floor(this.counter * 100 )/100);
        },
        complete: function () {
          $this.text(this.counter);
        }
      }
    );
  });