$(function() {
  $('.sticky-header').each(function() {
    if ($(this).find('thead').length > 0 && $(this).find('th').length > 0) {
      var $w = $(window);
      var $t = $(this);
      var $thead = $t.find('thead').clone();
      var $col = $t.find('thead, tbody').clone();

      $t
      .addClass('sticky-enabled')
      .css({
        margin: 0,
        width: '100%'
      }).wrap('<div class="sticky-wrap" />');

      $t.after('<table class="sticky-thead" />');

      if ($t.find('tbody th').length > 0) {
        $t.after('<table class="sticky-col" />');
      }

      var $stickyHead = $(this).siblings('.sticky-thead');
      var $stickyCol = $(this).siblings('.sticky-col');
      var $stickyWrap = $(this).parent('.sticky-wrap');

      $stickyHead.append($thead);

      var nCols = $t.find('tbody tr:eq(0) th').length;
      if (nCols == 0)
        nCols = 1;

      $stickyCol.append($col);
      $stickyCol.find('thead tr').each(function() {
        $(this).find('th:gt(' + (nCols - 1)  + ')').remove();
      });
      $stickyCol.find('tbody td').remove();

      var setWidths = function() {
        if ($t.width() > $stickyWrap.width()) {
          $stickyWrap.width($t.width());
        }

        $t
        .find('thead th').each(function(i) {
          $stickyHead.find('th').eq(i).width($(this).width());
        })
        .end()
        .find('tr').each(function(i) {
          $stickyCol.find('tr').eq(i).height($(this).height());
        });

        $stickyHead.width($t.width());

        $stickyCol.find('th').width($t.find('thead th').width())
      };

      var repositionStickyHead = function() {
        if ($w.scrollTop() > $t.offset().top &&
            $w.scrollTop() < $t.offset().top + $t.outerHeight()) {
          $stickyHead.css({
            opacity: 1,
            top: $w.scrollTop() - $t.offset().top
          });
        } else {
          $stickyHead.css({
            opacity: 0,
            top: 0
          });
        }
      };

      var repositionStickyCol = function() {
        if ($w.scrollLeft() > $t.offset().left &&
            $w.scrollLeft() < $t.offset().left + $t.outerWidth()) {
          var x = $w.scrollLeft() - $t.offset().left;
          $stickyCol.css({
            opacity: 1,
            left: $w.scrollLeft() - $t.offset().left
          });
        } else {
          $stickyCol.css({
            opacity: 0,
            left: 0
          });
        }
      };

      setWidths();

      $w
      .load(setWidths)
      .resize($.debounce(250, function() {
        setWidths();
        repositionStickyHead();
        repositionStickyCol();
      }))
      .scroll($.throttle(250, function() {
        repositionStickyHead();
        repositionStickyCol();
      }));
    }
  });
});
