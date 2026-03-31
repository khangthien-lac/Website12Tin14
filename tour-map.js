(function () {
  function getTourId() {
    var path = window.location.pathname;
    var filename = decodeURIComponent(path.split("/").pop());
    return filename.replace(".html", "").replace(".htm", "");
  }

  var mapInitialized = false;
  var mapInstance = null;
  var markerColors = [
    "#2E86DE", "#E74C3C", "#27AE60", "#F39C12", "#8E44AD",
    "#1ABC9C", "#E67E22", "#16A085", "#C0392B", "#2980B9",
  ];

  function createMap(containerId, waypoints) {
    var container = document.getElementById(containerId);
    if (!container) return;
    if (!waypoints || waypoints.length < 2) return;

    var map = L.map(containerId, {
      scrollWheelZoom: false,
      attributionControl: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 18,
    }).addTo(map);

    var markers = [];

    waypoints.forEach(function (wp, i) {
      var color = markerColors[i % markerColors.length];
      var icon = L.divIcon({
        className: "tour-marker",
        html:
          '<div style="background:' + color +
          ';color:#fff;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:14px;border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);">' +
          (i + 1) + "</div>",
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      var marker = L.marker([wp.lat, wp.lng], { icon: icon }).addTo(map);
      var dayInfo = wp.day ? "Ngày " + wp.day : "";
      var descInfo = wp.desc ? wp.desc : "";
      marker.bindPopup(
        "<b>" + wp.name + "</b><br>" +
        (dayInfo ? "<i>" + dayInfo + "</i><br>" : "") +
        (descInfo ? "<small>" + descInfo + "</small>" : "")
      );
      markers.push(marker);
    });

    // Filter consecutive duplicate waypoints
    var uniqueWaypoints = [];
    var lastLat = null, lastLng = null;
    waypoints.forEach(function (wp) {
      if (wp.lat !== lastLat || wp.lng !== lastLng) {
        uniqueWaypoints.push(wp);
        lastLat = wp.lat;
        lastLng = wp.lng;
      }
    });

    // Draw flight routes (straight lines within Vietnam)
    uniqueWaypoints.forEach(function (wp, i) {
      if (i < uniqueWaypoints.length - 1) {
        var nextWp = uniqueWaypoints[i + 1];
        var flightLine = L.polyline(
          [[wp.lat, wp.lng], [nextWp.lat, nextWp.lng]],
          { color: "#E74C3C", weight: 2, opacity: 0.8, dashArray: "8, 8" }
        ).addTo(map);
      }
    });

    // Main route line
    var routeLine = L.polyline(
      uniqueWaypoints.map(function (wp) { return [wp.lat, wp.lng]; }),
      { color: "#2E86DE", weight: 3, opacity: 0.6 }
    ).addTo(map);

    var allPoints = uniqueWaypoints.map(function (wp) { return [wp.lat, wp.lng]; });
    var bounds = L.latLngBounds(allPoints);
    map.fitBounds(bounds, { padding: [50, 50] });

    // Legend
    var legend = L.control({ position: "bottomright" });
    legend.onAdd = function () {
      var div = L.DomUtil.create("div", "tour-map-legend");
      var html = "<b>Lộ trình</b><br>";
      waypoints.forEach(function (wp, i) {
        var color = markerColors[i % markerColors.length];
        html +=
          '<span style="display:inline-block;width:10px;height:10px;background:' +
          color + ';border-radius:50%;margin-right:5px;"></span>' +
          (i + 1) + ". " + wp.name + "<br>";
      });
      div.innerHTML = html;
      return div;
    };
    legend.addTo(map);

    mapInstance = map;
    mapInitialized = true;
  }

  function buildDropdown(targetContainer, waypoints) {
    targetContainer.innerHTML = "";
    targetContainer.style.height = "auto";
    targetContainer.style.background = "transparent";
    targetContainer.style.borderRadius = "0";

    var mapContainer = document.createElement("div");
    mapContainer.style.marginBottom = "20px";
    
    var mapDiv = document.createElement("div");
    mapDiv.id = "tour-route-map";
    mapDiv.style.height = "400px";
    mapDiv.style.borderRadius = "12px";
    mapDiv.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
    mapContainer.appendChild(mapDiv);

    var listDiv = document.createElement("div");
    listDiv.className = "tour-route-list";
    listDiv.style.padding = "15px";
    listDiv.style.background = "#f8f9fa";
    listDiv.style.borderRadius = "8px";
    var listHTML = '<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;align-items:center;">';
    waypoints.forEach(function (wp, i) {
      var isFirst = i === 0;
      var isLast = i === waypoints.length - 1;
      var color = markerColors[i % markerColors.length];
      listHTML +=
        '<div style="display:flex;align-items:center;gap:5px;">' +
          '<span style="background:' + color + ';color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;">' + (i + 1) + '</span>' +
          '<span style="font-weight:bold;font-size:14px;">' + wp.name + '</span>' +
        '</div>';
      if (!isLast) {
        listHTML += '<span style="color:#999;">&#8594;</span>';
      }
    });
    listHTML += '</div>';
    listDiv.innerHTML = listHTML;

    targetContainer.appendChild(mapContainer);
    targetContainer.appendChild(listDiv);

    setTimeout(function () {
      createMap("tour-route-map", waypoints);
    }, 100);
  }

  function init() {
    var tourId = getTourId();
    var waypoints = null;

    if (typeof window.TOUR_ROUTE_WAYPOINTS !== "undefined") {
      waypoints = window.TOUR_ROUTE_WAYPOINTS;
    } else if (typeof window.TOUR_ROUTES_DATA !== "undefined") {
      var route = window.TOUR_ROUTES_DATA[tourId];
      if (route) waypoints = route.waypoints;
    }

    if (!waypoints) {
      try {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "tour-routes.json", false);
        xhr.send();
        if (xhr.status === 200 || xhr.status === 0) {
          var routes = JSON.parse(xhr.responseText);
          if (routes[tourId]) waypoints = routes[tourId].waypoints;
        }
      } catch (e) {}
    }

    if (!waypoints) return;

    var mapContainers = document.querySelectorAll(".footer-map");
    if (mapContainers.length === 0) return;

    var targetContainer = mapContainers[0];
    buildDropdown(targetContainer, waypoints);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
