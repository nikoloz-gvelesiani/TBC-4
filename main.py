from ext import app
from routes import homepage,search,login,logout,upload,edit_product,delete_product,card,about,gallery,search_gallery,register,add_to_cart,remove_item,cart_page,clear_cart

app.run(debug=True, host="0.0.0.0")
