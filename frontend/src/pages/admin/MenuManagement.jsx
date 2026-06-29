import { useEffect, useState } from "react";
import {
  createDailyMenu,
  createMenuItem,
  deleteMenuItem,
  getDailyMenus,
  getMenuItems,
  updateDailyMenu,
} from "../../api/endpoints";
import { getLocalDateString } from "../../utils/date";

const emptyForm = { name: "", description: "", category: "MAIN_COURSE", price: "", is_vegetarian: true };

export default function MenuManagement() {
  const [catalogItems, setCatalogItems] = useState([]);
  const [dailyMenus, setDailyMenus] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [selectedItemIds, setSelectedItemIds] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadCatalog();
    loadDailyMenus();
  }, []);

  async function loadCatalog() {
    const { data } = await getMenuItems();
    setCatalogItems(data.results || data);
  }

  async function loadDailyMenus() {
    const { data } = await getDailyMenus();
    setDailyMenus(data.results || data);
  }

  async function handleAddItem(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await createMenuItem(form);
      setForm(emptyForm);
      setMessage("Menu item added.");
      loadCatalog();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not add menu item.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeleteItem(id) {
    if (!confirm("Delete this menu item?")) return;
    try {
      await deleteMenuItem(id);
      loadCatalog();
    } catch (err) {
      setError("Could not delete item.");
    }
  }

  function toggleSelected(id) {
    setSelectedItemIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  }

  async function handlePublishToday(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const today = getLocalDateString();
      const payload = {
        date: today,
        is_published: true,
        items: selectedItemIds.map((id) => ({ menu_item_id: id })),
      };

      // If a daily menu for today already exists (e.g. from seeding, or a
      // previous publish), update it in place instead of trying to create
      // a duplicate, which the backend rejects since `date` is unique.
      const existing = dailyMenus.find((dm) => dm.date === today);
      if (existing) {
        await updateDailyMenu(existing.id, payload);
        setMessage("Today's menu updated.");
      } else {
        await createDailyMenu(payload);
        setMessage("Today's menu published.");
      }

      setSelectedItemIds([]);
      loadDailyMenus();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not publish menu.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto mt-6 px-4">
      <h1 className="text-xl font-bold mb-4">Menu Management</h1>

      {error && <p className="bg-red-50 text-red-700 text-sm p-2 rounded mb-3">{error}</p>}
      {message && <p className="bg-green-50 text-green-700 text-sm p-2 rounded mb-3">{message}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Catalog add form */}
        <div className="bg-white border border-gray-200 rounded p-4">
          <h2 className="font-semibold mb-3">Add Catalog Item</h2>
          <form onSubmit={handleAddItem} className="space-y-2">
            <input
              placeholder="Name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
            <textarea
              placeholder="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
            <div className="grid grid-cols-2 gap-2">
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="BREAKFAST">Breakfast</option>
                <option value="MAIN_COURSE">Main Course</option>
                <option value="SNACK">Snack</option>
                <option value="BEVERAGE">Beverage</option>
                <option value="DESSERT">Dessert</option>
              </select>
              <input
                type="number"
                step="0.01"
                placeholder="Price"
                required
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_vegetarian}
                onChange={(e) => setForm({ ...form, is_vegetarian: e.target.checked })}
              />
              Vegetarian
            </label>
            <button
              type="submit"
              disabled={submitting}
              className="bg-primary text-white px-4 py-2 rounded text-sm hover:bg-primary-dark disabled:opacity-50"
            >
              Add Item
            </button>
          </form>
        </div>

        {/* Publish today's menu */}
        <div className="bg-white border border-gray-200 rounded p-4">
          <h2 className="font-semibold mb-3">Publish Today's Menu</h2>
          <form onSubmit={handlePublishToday}>
            <div className="max-h-56 overflow-y-auto border border-gray-100 rounded mb-3">
              {catalogItems.map((item) => (
                <label key={item.id} className="flex items-center gap-2 px-3 py-2 text-sm border-b border-gray-50 last:border-0">
                  <input
                    type="checkbox"
                    checked={selectedItemIds.includes(item.id)}
                    onChange={() => toggleSelected(item.id)}
                  />
                  {item.name} (₹{Number(item.price).toFixed(2)})
                </label>
              ))}
            </div>
            <button
              type="submit"
              disabled={submitting || selectedItemIds.length === 0}
              className="bg-primary text-white px-4 py-2 rounded text-sm hover:bg-primary-dark disabled:opacity-50"
            >
              Publish Selected Items for Today
            </button>
          </form>
        </div>
      </div>

      {/* Catalog list */}
      <div className="bg-white border border-gray-200 rounded p-4 mt-6">
        <h2 className="font-semibold mb-3">Catalog ({catalogItems.length})</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-200">
              <th className="py-2">Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>Veg</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {catalogItems.map((item) => (
              <tr key={item.id} className="border-b border-gray-100">
                <td className="py-2">{item.name}</td>
                <td>{item.category}</td>
                <td>₹{Number(item.price).toFixed(2)}</td>
                <td>{item.is_vegetarian ? "Yes" : "No"}</td>
                <td className="text-right">
                  <button
                    onClick={() => handleDeleteItem(item.id)}
                    className="text-red-600 hover:underline text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Daily menus history */}
      <div className="bg-white border border-gray-200 rounded p-4 mt-6">
        <h2 className="font-semibold mb-3">Daily Menus</h2>
        <ul className="text-sm space-y-1">
          {dailyMenus.map((dm) => (
            <li key={dm.id} className="flex justify-between border-b border-gray-50 py-1">
              <span>{dm.date}</span>
              <span>{dm.is_published ? "Published" : "Draft"} — {dm.items.length} item(s)</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
