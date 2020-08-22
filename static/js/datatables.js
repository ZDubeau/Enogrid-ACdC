var validate = '<img src="/static/image/check.svg" style="height:18px;"/>';
var cancel = '<img src="/static/image/delete.png" style="height:18px;"/>';
var edit = '<img src="/static/image/edit.svg" style="height:18px;"/>';
var view = '<img src="/static/image/voir.svg" style="height:18px;"/>';
var download = '<img src="/static/image/download.svg" style="height:18px;"/>';
var hourglass = '<img src="/static/image/hourglass.svg" style="height:18px;"/>';
var error = '<img src="/static/image/error.svg" style="height:18px;"/>';
var not_started = '<img src="/static/image/not_started.svg" style="height:18px;"/>';

// Call the dataTables jQuery plugin
$(document).ready(function () {

  $('#dataTableProject').DataTable({
    "columnDefs": [
      { "visible": false, "targets": 0 },
      { "width": "55px", "targets": 1 },
      { "width": "45px", "targets": 2 },
      { "width": "45px", "targets": 3 },
      { "width": "20px", "targets": 4 },
      { "width": "20px", "targets": 5 },
      { "width": "20px", "targets": 6 },
      { "width": "25px", "targets": 7 },
      { "width": "25px", "targets": 8 },
    ],
    "columns": [
      { title: "" },
      { title: "Nom" },
      { title: "Nb production" },
      { title: "Nb consommation" },
      { title: "Editer" },
      { title: "Statut" },
      { title: "Afficher" },
      { title: "Télécharger" },
      { title: "Supprimer" }
    ],
    "order": [[0, "desc"]],
    "fnRowCallback": function (nRow, aData) {
      var status = Math.round(aData[5]);
      switch (status) {
        case 100:
          $('td:eq(4)', nRow).html(validate);
          break;
        case 80:
          $('td:eq(4)', nRow).html(hourglass);
          break;
        case 50:
          $('td:eq(4)', nRow).html(not_started);
          break;
        default:
          $('td:eq(4)', nRow).html(error);
      }
      var prod = aData[2];
      if (prod == "NaN") {
        $('td:eq(1)', nRow).html(0);
      } else {
        prod = Math.round(prod, 0)
        $('td:eq(1)', nRow).html(prod);
      }
      var conso = aData[3];
      if (conso == "NaN") {
        $('td:eq(2)', nRow).html(0);
      } else {
        conso = Math.round(conso, 0)
        $('td:eq(2)', nRow).html(conso);
      }

      $('td:eq(3)', nRow).html(edit);
      $('td:eq(3)', nRow).click(function () {
        var id = aData[0];
        window.location.href = '/project_edit/' + id;
      });
      if (status == "100") {
        $('td:eq(5)', nRow).html(view);
        $('td:eq(5)', nRow).click(function () {
          var id = aData[0];
          window.location.href = '/graph/' + id;
        });
        $('td:eq(6)', nRow).html(download);
        $('td:eq(6)', nRow).click(function () {
          var id = aData[0];
          window.location.href = '/download_files/' + id;
        });
      }

      $('td:eq(7)', nRow).html(cancel);
      $('td:eq(7)', nRow).click(function () {
        var id = aData[0];
        window.location.href = '/project_delete/' + id;
      });
    }
  });

  $('#dataTableProjectEditFiles').DataTable({
    "columnDefs": [
      { "visible": false, "targets": 0 },
      { "visible": false, "targets": 1 },
      { "width": "35px", "targets": 2 },
      { "width": "30px", "targets": 3 },
      { "width": "40px", "targets": 4 },
      { "width": "35px", "targets": 5 },
      { "width": "40px", "targets": 6 },
      { "width": "50px", "targets": 7 },
      { "width": "50px", "targets": 8 },
      { "width": "35px", "targets": 9 },
      { "width": "30px", "targets": 10 }
    ],
    "columns": [
      { title: "" },
      { title: "" },
      { title: "Nom" },
      { title: "Statut" },
      { title: "Template" },
      { title: "Type" },
      { title: "Longueur" },
      { title: "Normalisation" },
      { title: "Standardisation" },
      { title: "Télécharger" },
      { title: "Supprimer" }
    ],
    "order": [[0, "desc"]],
    "fnRowCallback": function (nRow, aData) {
      var id = aData[0];
      if (aData[3] == "Analysé") {
        $('td:eq(7)', nRow).html(download);
        $('td:eq(7)', nRow).click(function () {
          window.location.href = '/download_file/' + id;
        });
        $('td:eq(8)', nRow).html(cancel);
        $('td:eq(8)', nRow).click(function () {
          window.location.href = '/delete_file/' + id;
        });
      } else if (aData[3] == "Erreur") {
        $('td:eq(8)', nRow).html(cancel);
        $('td:eq(8)', nRow).click(function () {
          window.location.href = '/delete_file/' + id;
        });
      }
    }
  });

  $('#dataTableProjectEditAllFiles').DataTable({
    "columnDefs": [
      { "visible": false, "targets": 0 },
      { "width": "30px", "targets": 1 },
      { "width": "30px", "targets": 2 },
      { "width": "30px", "targets": 3 },
      { "width": "30px", "targets": 4 },
      { "width": "20px", "targets": 5 },
      { "width": "25px", "targets": 6 },
      { "width": "25px", "targets": 7 },
      { "width": "25px", "targets": 8 }
    ],
    "columns": [
      { title: "" },
      { title: "Nom" },
      { title: "Type" },
      { title: "Template" },
      { title: "kWh_normalisé" },
      { title: "kWh_standardisé" },
      { title: "Delta (ppb)" },
      { title: "Télécharger (nm)" },
      { title: "Télécharger (sd)" }
    ],
    "order": [[0, "desc"]],
    "fnRowCallback": function (nRow, aData) {
      var ppm = aData[5];
      switch (ppm) {
        case "NaN":
          $('td:eq(3)', nRow).html("");
          break;
        default:
          ppm = Math.abs(Math.round(ppm));
          $('td:eq(3)', nRow).html(ppm);
      }
      var id = aData[0];
      $('td:eq(6)', nRow).html(download);
      $('td:eq(6)', nRow).click(function () {
        window.location.href = '/download_file_normalise/' + id;
      });
      $('td:eq(7)', nRow).html(download);
      $('td:eq(7)', nRow).click(function () {
        window.location.href = '/download_file/' + id;
      });
    }
  });

  $('#validatedCustomFile').on('change', function () {
    var text = $(this).val();
    text = text.substring(text.lastIndexOf("\\") + 1, text.length);
    $(this).next('.custom-file-label').html(text);
  })

});