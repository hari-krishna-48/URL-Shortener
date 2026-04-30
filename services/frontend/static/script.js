let SHORTENER_SERVICE;
let AUTH_SERVICE;
let url = new URL(location.href);

if (url.port === "8002") {
    url.port = "8000";
    SHORTENER_SERVICE = url.origin;
    url.port = "8001";
    AUTH_SERVICE = url.origin;
} else {
    SHORTENER_SERVICE = `${url.origin}/shortener`;
    AUTH_SERVICE = `${url.origin}/auth`;
}

const $ = (query) => document.querySelector(query);
const $$ = (query) => document.querySelectorAll(query);

async function shortenUrl(url, token) {
    const response = await fetch(`${SHORTENER_SERVICE}/`, {
        method: "POST",
        body: JSON.stringify({
            value: url,
        }),
        headers: {
            Accept: "application/json",
            Authorization: token,
            "Content-type": "application/json",
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 400) {
        return { error: "URL is malformed", instance };
    } else if (response.status === 403) {
        return { error: "Invalid token", instance };
    }
    const { id } = await response.json();
    return { shortUrl: `${SHORTENER_SERVICE}/${id}`, instance };
}

$(".shorten").addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = $("[name=url]").value;
    const resultEl = $(".result");
    const token = $("[name=token]").value;
    const { shortUrl, instance, error } = await shortenUrl(url, token);
    $(".shorten .result-container-instance").innerText = `Instance: ${instance}`;
    if (!error) {
        resultEl.innerText = resultEl.href = shortUrl;
        $(".shorten .result-container").hidden = false;
        $(".shorten .result-container-error").hidden = true;
    } else {
        $(".shorten .result-container-error").innerText = error;
        $(".shorten .result-container").hidden = true;
        $(".shorten .result-container-error").hidden = false;
    }
});

async function editUrl(urlId, url, token) {
    const response = await fetch(`${SHORTENER_SERVICE}/${urlId}`, {
        method: "PUT",
        body: JSON.stringify({ url }),
        headers: {
            Accept: "application/json",
            Authorization: token,
            "Content-type": "application/json",
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 400) {
        return { error: "URL is malformed", instance };
    } else if (response.status === 404) {
        return { error: "ID does not exist", instance };
    } else if (response.status === 403) {
        return { error: "Invalid token", instance };
    }
    const { id } = await response.json();
    return { shortUrl: `${SHORTENER_SERVICE}/${id}`, instance };
}

$(".edit").addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = $("[name=new-url]").value;
    const id = $("[name=id]").value;
    const resultEl = $(".edit .result");
    const token = $("[name=token]").value;
    const { shortUrl, instance, error } = await editUrl(id, url, token);
    $(".edit .result-container-instance").innerText = `Instance: ${instance}`;
    if (!error) {
        resultEl.innerText = resultEl.href = shortUrl;
        $(".edit .result-container").hidden = false;
        $(".edit .result-container-error").hidden = true;
    } else {
        $(".edit .result-container-error").innerText = error;
        $(".edit .result-container").hidden = true;
        $(".edit .result-container-error").hidden = false;
    }
});

async function deleteUrl(urlId, token) {
    const response = await fetch(`${SHORTENER_SERVICE}/${urlId}`, {
        headers: {
            Authorization: token,
        },
        method: "DELETE",
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 404) {
        return { error: "ID does not exist", instance };
    } else if (response.status === 403) {
        return { error: "Invalid token", instance };
    }
    return { instance };
}

$(".delete").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = $("[name=del-id]").value;
    const token = $("[name=token]").value;
    const { error, instance } = await deleteUrl(id, token);
    $(".delete .result-container-instance").innerText = `Instance: ${instance}`;
    if (!error) {
        $(".delete .result-container").hidden = false;
        $(".delete .result-container-error").hidden = true;
    } else {
        $(".delete .result-container-error").innerText = error;
        $(".delete .result-container").hidden = true;
        $(".delete .result-container-error").hidden = false;
    }
});

async function deleteAll(token) {
    const response = await fetch(`${SHORTENER_SERVICE}/`, {
        method: "DELETE",
        headers: {
            Authorization: token,
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 403) {
        return { error: "Invalid token", instance };
    }
    return { instance };
}

$(".delete-all").addEventListener("click", async (e) => {
    e.preventDefault();
    const token = $("[name=token]").value;
    const { error, instance } = await deleteAll(token);
    $(".delete-all .result-container-instance").innerText =
        `Instance: ${instance}`;
    if (!error) {
        $(".delete .result-container").hidden = false;
        $(".delete .result-container-error").hidden = true;
    } else {
        $(".delete .result-container-error").innerText = error;
        $(".delete .result-container").hidden = true;
        $(".delete .result-container-error").hidden = false;
    }
});

async function loadUrls(token) {
    const response = await fetch(`${SHORTENER_SERVICE}/`, {
        headers: {
            Accept: "application/json",
            Authorization: token,
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    const { value } = await response.json();
    if (value === null) {
        return { urls: [], instance };
    } else {
        return { urls: value, instance };
    }
}

$(".load-urls").addEventListener("click", async (e) => {
    const token = $("[name=token]").value;
    const { urls, instance } = await loadUrls(token);
    $(".load-urls + .result-container-instance").innerText =
        `Instance: ${instance}`;
    const urlsList = $(".urls");
    urlsList.innerHTML = "";
    for (const url of urls) {
        const a = document.createElement("a");
        a.innerText = a.href = `${SHORTENER_SERVICE}/${url}`;
        const li = document.createElement("li");
        li.appendChild(a);
        urlsList.appendChild(li);
    }
});

async function login(username, password) {
    const response = await fetch(`${AUTH_SERVICE}/users/login`, {
        method: "POST",
        body: JSON.stringify({ username, password }),
        headers: {
            Accept: "application/json",
            "Content-type": "application/json",
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 403) {
        return { error: "Incorrect credentials", instance };
    }
    const { token } = await response.json();
    return { token, instance };
}

$(".login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = $("[name=username]").value;
    const password = $("[name=password]").value;
    const { token, error, instance } = await login(username, password);
    $(".login .result-container-instance").innerText = `Instance: ${instance}`;
    if (!error) {
        $(".login .result-container").hidden = false;
        $(".login .result-container").innerText = "Successfully logged in";
        $(".login .result-container-error").hidden = true;
        $("[name=token]").value = token;
    } else {
        $(".login .result-container-error").innerText = error;
        $(".login .result-container").hidden = true;
        $(".login .result-container-error").hidden = false;
    }
});

async function register(username, password) {
    const response = await fetch(`${AUTH_SERVICE}/users`, {
        method: "POST",
        body: JSON.stringify({ username, password }),
        headers: {
            Accept: "application/json",
            "Content-type": "application/json",
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 409) {
        return { error: "Username already exists", instance };
    }
    return { instance };
}

$(".register").addEventListener("click", async (e) => {
    e.preventDefault();
    const username = $("[name=username]").value;
    const password = $("[name=password]").value;
    const { error, instance } = await register(username, password);
    $(".login .result-container-instance").innerText = `Instance: ${instance}`;
    if (!error) {
        $(".login .result-container").hidden = false;
        $(".login .result-container").innerText = "Successfully registered";
        $(".login .result-container-error").hidden = true;
    } else {
        $(".login .result-container-error").innerText = error;
        $(".login .result-container").hidden = true;
        $(".login .result-container-error").hidden = false;
    }
});

async function verify(token) {
    const response = await fetch(`${AUTH_SERVICE}/auth/verify`, {
        method: "POST",
        headers: {
            Accept: "application/json",
            Authorization: token,
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 403) {
        return { error: "Token is invalid", instance };
    }
    const { payload } = await response.json();
    return { payload, instance };
}

$(".token").addEventListener("submit", async (e) => {
    e.preventDefault();
    const token = $("[name=token]").value;
    const { payload, error, instance } = await verify(token);
    $(".token .result-container-instance").innerText = `Instance: ${instance}`;
    if (!error) {
        $(".token .result-container").hidden = false;
        $(".token .result-container").innerText = `Welcome, ${payload.username}`;
        $(".token .result-container-error").hidden = true;
        $("[name=token]").value = token;
    } else {
        $(".token .result-container-error").innerText = error;
        $(".token .result-container").hidden = true;
        $(".token .result-container-error").hidden = false;
    }
});

async function updatePassword(username, oldPassword, newPassword) {
    const response = await fetch(`${AUTH_SERVICE}/users`, {
        method: "PUT",
        body: JSON.stringify({
            username,
            "old-password": oldPassword,
            "new-password": newPassword,
        }),
        headers: {
            Accept: "application/json",
            "Content-type": "application/json",
        },
    });
    const instance = response.headers.get("X-Instance-ID");
    if (response.status === 403) {
        return { error: "Incorrect credentials", instance };
    }
    return { instance };
}

$(".update-password").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = $("[name=username-update-pw]").value;
    const oldPassword = $("[name=old-password]").value;
    const newPassword = $("[name=new-password]").value;
    const { error, instance } = await updatePassword(
        username,
        oldPassword,
        newPassword,
    );
    $(".update-password .result-container-instance").innerText =
        `Instance: ${instance}`;
    if (!error) {
        $(".update-password .result-container").hidden = false;
        $(".update-password .result-container-error").hidden = true;
    } else {
        $(".update-password .result-container-error").innerText = error;
        $(".update-password .result-container").hidden = true;
        $(".update-password .result-container-error").hidden = false;
    }
});

$$(".origin").forEach((x) => (x.innerText = `${SHORTENER_SERVICE}/`));
