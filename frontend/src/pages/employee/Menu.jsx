import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getTodayMenu } from "../../api/endpoints";
import { useCart } from "../../context/CartContext";

export default function Menu() {
  const [menu, setMenu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { items, addItem, decreaseItem, totalAmount, totalCount } = useCart();
  const navigate = useNavigate();

  useEffect(() => {
    loadMenu();
  }, []);

  async function loadMenu() {
    setLoading(true);
    setError("");
    try {
      const { data } = await getTodayMenu();
      setMenu(data.menu);
    } catch (err) {
      setError("Could not load today's menu.");
    } finally {
      setLoading(false);
    }
  }

  function quantityInCart(menuItemId) {
    const found = items.find((i) => i.menu_item_id === menuItemId);
    return found ? found.quantity : 0;
  }

  if (loading) return <p className="text-center mt-10 text-gray-500">Loading menu...</p>;
  if (error) return <p className="text-center mt-10 text-red-600">{error}</p>;

  if (!menu) {
    return (
      <div className="max-w-xl mx-auto mt-12 text-center text-gray-600">
        <p>No menu has been published for today yet. Please check back later.</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto mt-6 px-4">
      <h1 className="text-xl font-bold mb-1">Today's Menu — {menu.date}</h1>
      <p className="text-sm text-gray-500 mb-6">
        {menu.is_order_open ? "Ordering is open." : "Ordering for today is closed."}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {menu.items.map((listing) => {
          const qty = quantityInCart(listing.menu_item.id);
          return (
            <div key={listing.id} className="border border-gray-200 rounded p-4 bg-white">
              <div className="flex justify-between items-start">
                <h2 className="font-semibold">{listing.menu_item.name}</h2>
                <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                  {listing.menu_item.is_vegetarian ? "Veg" : "Non-Veg"}
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-1">{listing.menu_item.description}</p>
              <div className="flex justify-between items-center mt-3">
                <span className="font-medium">₹{Number(listing.effective_price).toFixed(2)}</span>
                {listing.is_sold_out ? (
                  <span className="text-sm text-red-600">Sold out</span>
                ) : qty === 0 ? (
                  <button
                    onClick={() => addItem({ id: listing.menu_item.id, name: listing.menu_item.name, price: listing.effective_price })}
                    className="bg-primary text-white text-sm px-3 py-1.5 rounded hover:bg-primary-dark"
                  >
                    Add to Cart
                  </button>
                ) : (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => decreaseItem(listing.menu_item.id)}
                      className="bg-gray-200 px-2 py-1 rounded"
                    >
                      −
                    </button>
                    <span>{qty}</span>
                    <button
                      onClick={() => addItem({ id: listing.menu_item.id, name: listing.menu_item.name, price: listing.effective_price })}
                      className="bg-gray-200 px-2 py-1 rounded"
                    >
                      +
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {totalCount > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 flex justify-between items-center">
          <span className="text-sm text-gray-700">
            {totalCount} item(s) — ₹{totalAmount.toFixed(2)}
          </span>
          <button
            onClick={() => navigate("/checkout")}
            className="bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark"
          >
            Go to Checkout
          </button>
        </div>
      )}
    </div>
  );
}
