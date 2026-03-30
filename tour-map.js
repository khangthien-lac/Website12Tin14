(function () {
  function getTourId() {
    var path = window.location.pathname;
    var filename = decodeURIComponent(path.split("/").pop());
    return filename.replace(".html", "").replace(".htm", "");
  }

  var mapInitialized = false;
  var mapInstance = null;

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

    var markerColors = [
      "#2E86DE", "#E74C3C", "#27AE60", "#F39C12", "#8E44AD",
      "#1ABC9C", "#E67E22", "#16A085", "#C0392B", "#2980B9",
    ];
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
      marker.bindPopup(
        "<b>Điểm " + (i + 1) + " / " + waypoints.length + "</b><br>" +
        wp.name +
        (i === 0 ? "<br><i>Khởi hành</i>" :
         i === waypoints.length - 1 ? "<br><i>Điểm cuối</i>" : "")
      );
      markers.push(marker);
    });

    // Dashed line fallback
    var polyline = L.polyline(
      waypoints.map(function (wp) { return [wp.lat, wp.lng]; }),
      { color: "#2E86DE", weight: 4, opacity: 0.7, dashArray: "10, 10" }
    ).addTo(map);

    var allPoints = waypoints.map(function (wp) { return [wp.lat, wp.lng]; });
    var bounds = L.latLngBounds(allPoints);
    map.fitBounds(bounds, { padding: [40, 40] });

    // OSRM driving route
    try {
      var coordString = waypoints.map(function (wp) {
        return wp.lng + "," + wp.lat;
      }).join(";");

      var url =
        "https://router.project-osrm.org/route/v1/driving/" +
        coordString + "?overview=full&geometries=geojson";

      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.onload = function () {
        if (xhr.status === 200) {
          try {
            var data = JSON.parse(xhr.responseText);
            if (data.code === "Ok" && data.routes && data.routes.length > 0) {
              var route = data.routes[0];
              var coordinates = route.geometry.coordinates.map(function (c) {
                return [c[1], c[0]];
              });
              map.removeLayer(polyline);
              var routeLine = L.polyline(coordinates, {
                color: "#2E86DE", weight: 4, opacity: 0.8,
              }).addTo(map);

              var newBounds = routeLine.getBounds();
              markers.forEach(function (m) { newBounds.extend(m.getLatLng()); });
              map.fitBounds(newBounds, { padding: [40, 40] });
            }
          } catch (e) {}
        }
      };
      xhr.send();
    } catch (e) {}

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
    // Build dropdown HTML
    targetContainer.innerHTML = "";

    // Override parent .footer-map fixed height/background
    targetContainer.style.height = "auto";
    targetContainer.style.background = "transparent";
    targetContainer.style.borderRadius = "0";

    var wrapper = document.createElement("div");
    wrapper.className = "tour-route-dropdown";

    var header = document.createElement("div");
    header.className = "tour-route-header";
    header.innerHTML =
      '<span class="tour-route-title">' +
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:8px;">' +
          '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>' +
          '<circle cx="12" cy="10" r="3"></circle>' +
        '</svg>Lộ trình tour</span>' +
      '<span class="tour-route-arrow">&#9660;</span>';

    var body = document.createElement("div");
    body.className = "tour-route-body";

    var mapDiv = document.createElement("div");
    mapDiv.id = "tour-route-map";
    body.appendChild(mapDiv);

    // Waypoint list
    var listDiv = document.createElement("div");
    listDiv.className = "tour-route-list";
    var listHTML = '<div class="tour-route-steps">';
    waypoints.forEach(function (wp, i) {
      var isFirst = i === 0;
      var isLast = i === waypoints.length - 1;
      var stepClass = isFirst ? "step-start" : isLast ? "step-end" : "step-mid";
      listHTML +=
        '<div class="tour-route-step ' + stepClass + '">' +
          '<div class="step-dot">' + (i + 1) + '</div>' +
          '<div class="step-info">' +
            '<span class="step-name">' + wp.name + '</span>' +
            (isFirst ? '<span class="step-badge start">Khởi hành</span>' :
             isLast ? '<span class="step-badge end">Điểm cuối</span>' :
             '<span class="step-badge mid">Ngày ' + (i + 1) + '</span>') +
          '</div>' +
        '</div>';
      if (!isLast) {
        listHTML += '<div class="step-connector"></div>';
      }
    });
    listHTML += '</div>';
    listDiv.innerHTML = listHTML;
    body.appendChild(listDiv);

    wrapper.appendChild(header);
    wrapper.appendChild(body);
    targetContainer.appendChild(wrapper);

    // Toggle
    header.addEventListener("click", function () {
      var isOpen = wrapper.classList.contains("open");
      wrapper.classList.toggle("open");

      if (!isOpen && !mapInitialized) {
        setTimeout(function () {
          createMap("tour-route-map", waypoints);
        }, 100);
      } else if (!isOpen && mapInstance) {
        setTimeout(function () {
          mapInstance.invalidateSize();
        }, 350);
      }
    });
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
