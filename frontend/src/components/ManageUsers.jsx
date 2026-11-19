
import { useEffect, useState } from 'react';

import {
  Plus,
  RefreshCcw,
  UserRoundCheck,
  UserRoundX,
} from 'lucide-react';

import { api } from '../api.js';


const branches = [
  {
    value: 'liberty',
    label: 'Liberty Plaza, Kollupitiya',
  },
  {
    value: 'galle_face',
    label: 'One Galle Face Mall',
  },
  {
    value: 'pettah',
    label: 'Pettah Main Street',
  },
];


const emptyForm = {
  full_name: '',
  username: '',
  password: '',
  branch: 'liberty',
};


function getErrorMessage(error) {
  const detail =
    error?.response?.data?.detail ??
    error?.detail ??
    error?.message ??
    error;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc)
          ? item.loc.filter((part) => part !== 'body').join('.')
          : '';

        const message = item?.msg || 'Invalid input';

        return field
          ? `${field}: ${message}`
          : message;
      })
      .join('. ');
  }

  if (detail && typeof detail === 'object') {
    if (typeof detail.msg === 'string') {
      return detail.msg;
    }

    if (typeof detail.message === 'string') {
      return detail.message;
    }

    if (typeof detail.error === 'string') {
      return detail.error;
    }

    return 'The request could not be completed. Please check your details.';
  }

  return 'Something went wrong. Please try again.';
}


export default function ManageUsers() {
  const [users, setUsers] = useState([]);

  const [form, setForm] = useState(emptyForm);

  const [showForm, setShowForm] = useState(false);

  const [error, setError] = useState('');

  const [notice, setNotice] = useState('');

  const [busy, setBusy] = useState(false);

  const [loading, setLoading] = useState(true);


  async function refresh() {
    try {
      const result = await api('/managers');

      setUsers(
        Array.isArray(result) ? result : []
      );

      return true;

    } catch (reason) {
      console.error('Failed to load managers:', reason);

      setError(getErrorMessage(reason));

      return false;
    }
  }


  useEffect(() => {
    let active = true;

    async function loadManagers() {
      setLoading(true);

      try {
        const result = await api('/managers');

        if (active) {
          setUsers(
            Array.isArray(result) ? result : []
          );
        }

      } catch (reason) {
        console.error('Failed to load managers:', reason);

        if (active) {
          setError(getErrorMessage(reason));
        }

      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadManagers();

    return () => {
      active = false;
    };
  }, []);


  function updateForm(field, value) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  }


  function openForm() {
    setError('');

    setNotice('');

    setShowForm(true);
  }


  function closeForm() {
    setShowForm(false);

    setForm({ ...emptyForm });

    setError('');
  }


  async function create(event) {
    event.preventDefault();

    if (busy) {
      return;
    }

    setBusy(true);

    setError('');

    setNotice('');

    const payload = {
      full_name: form.full_name.trim(),
      username: form.username.trim(),
      password: form.password,
      branch: form.branch,
    };

    if (payload.full_name.length < 2) {
      setError('Please enter a valid full name.');

      setBusy(false);

      return;
    }

    if (payload.username.length < 3) {
      setError('Username must contain at least 3 characters.');

      setBusy(false);

      return;
    }

    if (payload.password.length < 8) {
      setError('Temporary password must contain at least 8 characters.');

      setBusy(false);

      return;
    }

    try {
      await api('/managers', {
        method: 'POST',

        body: JSON.stringify(payload),
      });

      setForm({ ...emptyForm });

      setShowForm(false);

      setNotice(
        'Manager account created successfully. ' +
        'Please share the temporary password privately.'
      );

      await refresh();

    } catch (reason) {
      console.error('Manager creation failed:', reason);

      setError(getErrorMessage(reason));

    } finally {
      setBusy(false);
    }
  }


  async function update(manager, changes) {
    setError('');

    setNotice('');

    try {
      await api(`/managers/${manager.id}`, {
        method: 'PATCH',

        body: JSON.stringify(changes),
      });

      setNotice(
        'Manager account updated successfully. ' +
        'Existing sessions have been revoked.'
      );

      await refresh();

    } catch (reason) {
      console.error('Manager update failed:', reason);

      setError(getErrorMessage(reason));

      await refresh();
    }
  }


  async function reset(manager) {
    const password = window.prompt(
      `Enter a new temporary password for ${manager.name} ` +
      '(minimum 8 characters):'
    );

    if (password === null || password === '') {
      return;
    }

    if (password.length < 8) {
      setError(
        'Temporary password must contain at least 8 characters.'
      );

      return;
    }

    setError('');

    setNotice('');

    try {
      await api(
        `/managers/${manager.id}/reset-password`,
        {
          method: 'POST',

          body: JSON.stringify({
            new_password: password,
          }),
        }
      );

      setNotice(
        'Password reset successfully. ' +
        'The manager must change it after signing in.'
      );

    } catch (reason) {
      console.error('Password reset failed:', reason);

      setError(getErrorMessage(reason));
    }
  }


  return (
    <div className="page-wrap">

      <header className="page-header">

        <div className="eyebrow">
          OWNER ACCESS ONLY
        </div>

        <div className="header-flex">

          <div>
            <h1>Manage Users</h1>

            <p>
              Create and manage branch manager access.
            </p>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={() => {
              if (showForm) {
                closeForm();
              } else {
                openForm();
              }
            }}
          >
            <Plus size={17} />

            {showForm ? 'Close form' : 'Add manager'}
          </button>

        </div>

      </header>


      {error && (
        <div
          className="error-banner"
          role="alert"
        >
          {error}
        </div>
      )}


      {notice && (
        <div
          className="success-banner"
          role="status"
        >
          {notice}
        </div>
      )}


      {showForm && (
        <form
          className="panel manager-form"
          onSubmit={create}
        >

          <h2>New manager account</h2>

          <div className="form-grid">

            <label>
              Full name

              <input
                required
                minLength={2}
                value={form.full_name}
                placeholder="e.g. Mohamed Ihshan"
                onChange={(event) => {
                  updateForm(
                    'full_name',
                    event.target.value
                  );
                }}
              />
            </label>


            <label>
              Username

              <input
                required
                minLength={3}
                value={form.username}
                placeholder="e.g. ihshan.liberty"
                autoComplete="off"
                onChange={(event) => {
                  updateForm(
                    'username',
                    event.target.value
                  );
                }}
              />
            </label>


            <label>
              Assigned branch

              <select
                value={form.branch}
                onChange={(event) => {
                  updateForm(
                    'branch',
                    event.target.value
                  );
                }}
              >
                {branches.map((branch) => (
                  <option
                    key={branch.value}
                    value={branch.value}
                  >
                    {branch.label}
                  </option>
                ))}
              </select>
            </label>


            <label>
              Temporary password

              <input
                required
                type="password"
                minLength={8}
                value={form.password}
                placeholder="Minimum 8 characters"
                autoComplete="new-password"
                onChange={(event) => {
                  updateForm(
                    'password',
                    event.target.value
                  );
                }}
              />
            </label>

          </div>


          <div className="form-actions">

            <button
              type="submit"
              className="primary-button"
              disabled={busy}
            >
              {busy ? 'Creating...' : 'Create account'}
            </button>

            <button
              type="button"
              className="outline-button"
              onClick={closeForm}
              disabled={busy}
            >
              Cancel
            </button>

          </div>

        </form>
      )}


      <section className="panel">

        <div className="panel-heading">

          <div>
            <h2>Branch managers</h2>

            <p>
              {loading
                ? 'Loading manager accounts...'
                : `${users.length} registered managers · Only the owner can administer accounts`
              }
            </p>
          </div>

          <button
            type="button"
            className="outline-button"
            onClick={refresh}
            title="Refresh manager accounts"
          >
            <RefreshCcw size={15} />

            Refresh
          </button>

        </div>


        <div className="table-scroll">

          <table className="data-table">

            <thead>
              <tr>
                <th>Name</th>

                <th>Username</th>

                <th>Assigned branch</th>

                <th>Status</th>

                <th>Actions</th>
              </tr>
            </thead>


            <tbody>

              {users.map((manager) => (

                <tr key={manager.id}>

                  <td>
                    <strong>
                      {manager.name}
                    </strong>
                  </td>


                  <td>
                    {manager.username}
                  </td>


                  <td>
                    <select
                      aria-label={`Branch for ${manager.name}`}
                      value={manager.branch}
                      onChange={(event) => {
                        update(manager, {
                          branch: event.target.value,
                        });
                      }}
                    >
                      {branches.map((branch) => (
                        <option
                          key={branch.value}
                          value={branch.value}
                        >
                          {branch.label}
                        </option>
                      ))}
                    </select>
                  </td>


                  <td>
                    <span
                      className={
                        `status ${manager.active
                          ? 'active'
                          : 'inactive'
                        }`
                      }
                    >
                      {manager.active
                        ? 'Active'
                        : 'Disabled'
                      }
                    </span>
                  </td>


                  <td>
                    <div className="action-buttons">

                      <button
                        type="button"
                        title="Reset password"
                        aria-label={`Reset password for ${manager.name}`}
                        onClick={() => reset(manager)}
                      >
                        <RefreshCcw size={15} />
                      </button>


                      <button
                        type="button"
                        title={
                          manager.active
                            ? 'Deactivate'
                            : 'Activate'
                        }
                        aria-label={
                          manager.active
                            ? `Deactivate ${manager.name}`
                            : `Activate ${manager.name}`
                        }
                        onClick={() => {
                          update(manager, {
                            active: !manager.active,
                          });
                        }}
                      >
                        {manager.active ? (
                          <UserRoundX size={17} />
                        ) : (
                          <UserRoundCheck size={17} />
                        )}
                      </button>

                    </div>
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>


        {!loading && users.length === 0 && (
          <p className="empty-row">
            No managers yet. Add your first branch manager above.
          </p>
        )}

      </section>


      <p className="fineprint">
        Accounts use hashed passwords.
        Manager sessions are revoked after account changes.
        No public signup is available.
      </p>

    </div>
  );
}
